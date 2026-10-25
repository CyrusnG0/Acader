"""Durable receipts and artifacts (T-018): atomic issuance, retry, restart, rebuild and deletion.

These tests use ROOM_LLM=stub and the same in-memory/temporary SQLite conventions as the rest
of the app. No model is contacted.
"""
import pytest

from app.events_service import EventService
from app.receipt_service import _persist, issue_receipt
from app.receipt_store import (CorruptArtifact, CorruptReceipt, ReceiptConflict, ReceiptStore)
from engine.events import canonical_json, sha256_hex
from engine.provenance import InMemorySources
from engine.receipt import compile_receipt
from tests.test_receipt_compile import BLOCK_TEXT, FIXED_STAMP, LOG, parts, rich_log, set_doc
from tests.test_replay_compile import Clock, Writer

SECOND = "L2"


@pytest.fixture(autouse=True)
def _stub(monkeypatch):
    monkeypatch.setenv("ROOM_LLM", "stub")


def build_log(svc, clock, log_id: str) -> InMemorySources:
    """A sealed log with one claim, one declared claim and a source, so questions and
    artifacts are produced by the stub compiler."""
    w = Writer(svc, clock, log_id)

    def add(type_, actor, **payload):
        return svc.append_event(log_id, type=type_, actor=actor, payload=payload)

    add("source.add", "teacher", source_id="s1", origin="teacher",
        title="Fluid balance study", url=None)
    add("card.create", "student", card_id="c1", text="Fluids matter",
        origin_runs=[{"from": 0, "to": 13, "kind": "typed"}], via="typed", via_ref=None)
    add("card.anchor", "student", card_id="c1", source_id="s1", block_id="b1")
    add("claim.create", "student", claim_id="k1", text="Fluid balance needs checking",
        card_ids=["c1"], parent_claim_id=None)
    add("import.declared", "student", import_id="i1", tool_name="ChatGPT",
        raw_text_ref="r1", size_chars=120)
    add("claim.extracted", "system", claim_id="kd", text="Intake should be capped",
        import_id="i1")
    set_doc(w, [
        ("Fluid balance needs checking every shift.", ["k1"], "typed", None),
        ("Intake should be capped for frail patients.", ["kd"], "typed", None),
        ("So the closing claim rests on my own reading.", [], "typed", None)])
    w.checkpoint()
    w.submit()
    return InMemorySources(blocks={"b1": BLOCK_TEXT}, helper={})


def issued(service, sources, log_id=LOG, **kwargs):
    return issue_receipt(service, log_id, sources, stamp=FIXED_STAMP, **kwargs)


def receipt_events(service, log_id=LOG):
    return [e for e in service.events(log_id) if e["type"] == "receipt.issued"]


# ---------------------------------------------------------------- persistence and integrity
def test_issue_persists_canonical_bytes_hash_and_artifacts():
    svc, sources = rich_log()
    res, ev = issued(svc, sources)
    store = ReceiptStore(svc.db)
    seal = res.receipt["seal_hash"]

    stored = store.get(LOG, seal_hash=seal)
    assert stored is not None
    assert stored.receipt_id == res.receipt["receipt_id"]
    assert stored.seal_seq == res.receipt["seal_seq"]
    assert stored.version == 1
    assert stored.receipt_hash == res.receipt_hash == sha256_hex(canonical_json(res.receipt))
    assert stored.body == canonical_json(res.receipt)
    assert stored.receipt == res.receipt
    assert store.stored_artifacts(LOG) == res.artifacts
    assert store.latest(LOG).receipt_hash == res.receipt_hash

    assert ev["type"] == "receipt.issued" and ev["payload"] == res.issued_payload()
    assert receipt_events(svc) == [ev]
    checked = store.verify(LOG, seal_hash=seal)
    assert checked.ok, checked.problems


def test_restart_persistence(tmp_path):
    path = str(tmp_path / "room.db")
    clock = Clock()
    svc = EventService(path, clock)
    sources = build_log(svc, clock, LOG)
    res, _ = issued(svc, sources)
    assert res.artifacts
    seal = res.receipt["seal_hash"]
    svc.close()

    again = EventService(path)
    store = ReceiptStore(again.db)
    stored = store.get(LOG, seal_hash=seal)
    assert stored is not None and stored.body == canonical_json(res.receipt)
    assert store.stored_artifacts(LOG) == res.artifacts
    checked = store.verify(LOG, seal_hash=seal)
    assert checked.ok, checked.problems
    again.close()


def test_rollback_on_failed_issuance(monkeypatch):
    svc, sources = rich_log()
    store = ReceiptStore(svc.db)
    real_append = svc.store.append_in_tx

    def fail(log_id, *, type, **kwargs):
        if type == "receipt.issued":
            raise RuntimeError("event write failed")
        return real_append(log_id, type=type, **kwargs)

    monkeypatch.setattr(svc.store, "append_in_tx", fail)
    with pytest.raises(RuntimeError):
        issued(svc, sources)

    assert store.get(LOG) is None
    assert store.artifacts(LOG) == {}
    assert receipt_events(svc) == []
    # the log itself is unchanged and still sealed
    assert svc.verify(LOG)["ok"]


def test_retry_is_idempotent_and_makes_no_model_calls():
    svc, sources = rich_log()
    first, event = issued(svc, sources)
    store = ReceiptStore(svc.db)
    before_events = svc.events(LOG)
    before_artifacts = store.artifacts(LOG)

    def forbidden(_messages):
        raise AssertionError("a retry attempted a model call")

    second, again = issued(svc, sources, ask=forbidden)
    assert canonical_json(second.receipt) == canonical_json(first.receipt)
    assert second.receipt_hash == first.receipt_hash
    assert second.artifacts == first.artifacts
    assert again["seq"] == event["seq"]
    assert svc.events(LOG) == before_events
    assert store.artifacts(LOG) == before_artifacts
    assert len(receipt_events(svc)) == 1
    assert store.store(LOG, receipt=first.receipt, receipt_hash=first.receipt_hash,
                       artifacts=first.artifacts) is False


def test_stored_output_rebuild_is_byte_identical_without_a_model():
    svc, sources = rich_log()
    first, _ = issued(svc, sources)
    store = ReceiptStore(svc.db)
    stored = store.stored_artifacts(LOG)
    assert stored == first.artifacts

    def forbidden(_messages):
        raise AssertionError("stored-output rebuild attempted a model call")

    rebuilt = compile_receipt(ask=forbidden, stored=stored, **parts(svc, sources))
    assert canonical_json(rebuilt.receipt) == canonical_json(first.receipt)
    assert rebuilt.receipt_hash == first.receipt_hash
    assert rebuilt.artifacts == first.artifacts


def test_no_write_transaction_during_a_model_call():
    svc, sources = rich_log()
    calls = []

    def ask(messages):
        assert svc.db.in_transaction is False
        calls.append(messages)
        from app.receipt_service import llm_ask
        return llm_ask(messages)

    issued(svc, sources, ask=ask)
    assert calls


# ---------------------------------------------------------------- rejection
def test_corrupt_receipt_is_rejected():
    svc, sources = rich_log()
    res, _ = issued(svc, sources)
    store = ReceiptStore(svc.db)
    seal = res.receipt["seal_hash"]
    svc.db.execute(
        "UPDATE receipts SET body = ? WHERE log_id = ? AND seal_hash = ? AND version = 1",
        (canonical_json(res.receipt) + b" ", LOG, seal))
    with pytest.raises(CorruptReceipt):
        store.get(LOG, seal_hash=seal)
    checked = store.verify(LOG, seal_hash=seal)
    assert not checked.ok and any("canonical" in p for p in checked.problems)


def test_receipt_hash_mismatch_is_rejected():
    svc, sources = rich_log()
    res, _ = issued(svc, sources)
    store = ReceiptStore(svc.db)
    seal = res.receipt["seal_hash"]
    svc.db.execute(
        "UPDATE receipts SET receipt_hash = ? "
        "WHERE log_id = ? AND seal_hash = ? AND version = 1", ("0" * 64, LOG, seal))
    with pytest.raises(CorruptReceipt):
        store.get(LOG, seal_hash=seal)
    assert not store.verify(LOG, seal_hash=seal).ok


def test_missing_receipt_is_rejected():
    svc, sources = rich_log()
    res, _ = issued(svc, sources)
    store = ReceiptStore(svc.db)
    seal = res.receipt["seal_hash"]
    svc.db.execute("DELETE FROM receipts WHERE log_id = ?", (LOG,))
    assert store.get(LOG, seal_hash=seal) is None
    assert not store.verify(LOG, seal_hash=seal).ok


def test_corrupt_artifact_is_rejected():
    svc, sources = rich_log()
    res, _ = issued(svc, sources)
    store = ReceiptStore(svc.db)
    aid = sorted(res.artifacts)[0]
    svc.db.execute(
        "UPDATE receipt_artifacts SET body = body || ? WHERE log_id = ? AND artifact_id = ?",
        (" ", LOG, aid))
    with pytest.raises(CorruptArtifact):
        store.stored_artifacts(LOG)
    checked = store.verify(LOG)
    assert not checked.ok
    assert any(aid in p for p in checked.problems)


def test_missing_artifact_is_rejected():
    svc, sources = rich_log()
    res, _ = issued(svc, sources)
    store = ReceiptStore(svc.db)
    aid = sorted(res.artifacts)[0]
    svc.db.execute("DELETE FROM receipt_artifacts WHERE log_id = ? AND artifact_id = ?",
                   (LOG, aid))
    checked = store.verify(LOG)
    assert not checked.ok
    assert any(aid in p for p in checked.problems)


def test_verify_accepts_outputs_supplied_by_the_caller():
    """T-020 can pass mapper artifacts alongside the stored compile outputs."""
    svc, sources = rich_log()
    res, _ = issued(svc, sources)
    store = ReceiptStore(svc.db)
    aid = sorted(res.artifacts)[0]
    artifact = store.artifacts(LOG)[aid]
    svc.db.execute("DELETE FROM receipt_artifacts WHERE log_id = ? AND artifact_id = ?",
                   (LOG, aid))
    assert not store.verify(LOG).ok
    checked = store.verify(LOG, extra_artifacts={aid: artifact})
    assert checked.ok, checked.problems


def test_verify_rejects_a_supplied_artifact_that_collides_with_a_stored_row():
    """A caller-supplied output must never replace (and so hide) a damaged stored row."""
    svc, sources = rich_log()
    res, _ = issued(svc, sources)
    store = ReceiptStore(svc.db)
    aid = sorted(res.artifacts)[0]
    good = store.artifacts(LOG)[aid]
    svc.db.execute(
        "UPDATE receipt_artifacts SET body = body || ? WHERE log_id = ? AND artifact_id = ?",
        (" ", LOG, aid))
    assert not store.verify(LOG).ok
    with pytest.raises(ReceiptConflict):
        store.verify(LOG, extra_artifacts={aid: good})


def test_concurrent_issuance_with_a_different_stamp_returns_the_first_receipt():
    """PD-T018-1 across the pre-check race: the first stored issuance wins."""
    svc, sources = rich_log()
    first, first_event = issued(svc, sources)
    store = ReceiptStore(svc.db)
    other_stamp = {**FIXED_STAMP, "git_sha": "other-sha"}
    other = parts(svc, sources)
    other["stamp"] = other_stamp
    second = compile_receipt(ask=None, stored=store.stored_artifacts(LOG), **other)
    assert second.receipt_hash != first.receipt_hash  # the stamp is part of the receipt

    # Both callers passed the pre-check before either wrote; the transaction resolves it.
    returned, event = _persist(svc, store, LOG, second, version=1)
    assert returned.receipt_hash == first.receipt_hash
    assert canonical_json(returned.receipt) == canonical_json(first.receipt)
    assert event["seq"] == first_event["seq"]
    assert len(receipt_events(svc)) == 1
    assert store.get(LOG, seal_hash=first.receipt["seal_hash"]).receipt_hash == first.receipt_hash
    assert store.artifacts(LOG) == first.artifacts

    retry, retry_event = issue_receipt(svc, LOG, sources, stamp=other_stamp)
    assert retry.receipt_hash == first.receipt_hash
    assert retry_event["seq"] == first_event["seq"]


def test_store_rejects_a_mismatched_hash_and_a_bad_artifact():
    svc, _ = rich_log()
    store = ReceiptStore(svc.db)
    receipt = {"log_id": "L9", "receipt_id": "r_" + "0" * 16, "version": 1,
               "seal_hash": "b" * 64, "seal_seq": 3}
    digest = sha256_hex(canonical_json(receipt))
    with pytest.raises(ReceiptConflict):
        store.store("L9", receipt=receipt, receipt_hash="0" * 64)
    assert store.get("L9", seal_hash="b" * 64) is None

    body = "{}"
    bad = {"a_1": {"artifact_id": "a_1", "task": "receipt_question", "prompt_hash": "p",
                   "body": body, "hash": "0" * 64}}
    with pytest.raises(CorruptArtifact):
        store.store("L9", receipt=receipt, receipt_hash=digest, artifacts=bad)
    assert store.get("L9", seal_hash="b" * 64) is None and store.artifacts("L9") == {}


def test_conflicting_receipt_under_the_same_key_is_rejected():
    svc, sources = rich_log()
    res, _ = issued(svc, sources)
    store = ReceiptStore(svc.db)
    changed = {**res.receipt, "summary": {**res.receipt["summary"], "text": "x"}}
    with pytest.raises(ReceiptConflict):
        store.store(LOG, receipt=changed)
    stored = store.get(LOG, seal_hash=res.receipt["seal_hash"])
    assert stored.receipt == res.receipt


# ---------------------------------------------------------------- isolation
def test_cross_log_isolation():
    clock = Clock()
    svc = EventService(":memory:", clock)
    a_sources = build_log(svc, clock, LOG)
    b_sources = build_log(svc, clock, SECOND)
    a, _ = issued(svc, a_sources, LOG)
    b, _ = issued(svc, b_sources, SECOND)
    store = ReceiptStore(svc.db)
    a_seal, b_seal = a.receipt["seal_hash"], b.receipt["seal_hash"]
    assert a_seal != b_seal

    assert store.get(LOG, seal_hash=a_seal).receipt_id == a.receipt["receipt_id"]
    assert store.get(LOG, seal_hash=b_seal) is None
    assert store.get(SECOND, seal_hash=b_seal).receipt_id == b.receipt["receipt_id"]
    assert store.get(SECOND, seal_hash=a_seal) is None
    assert store.verify(LOG, seal_hash=a_seal).ok
    assert store.verify(SECOND, seal_hash=b_seal).ok
    assert store.get(SECOND, seal_hash=b_seal) is not None
