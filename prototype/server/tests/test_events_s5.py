"""Spike S5: the log is tamper-evident (event-log.md §6, evaluation.md §1)."""
import copy
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from engine.events import (POST_SEAL_WHITELIST, CanonicalError, EventStore, SealedError,
                           build_event, canonical_json, event_hash, genesis_prev_hash,
                           sha256_hex, verify)

SERVER = Path(__file__).resolve().parents[1]
LOG = "log-s5"
TS = "2026-11-02T14:00:00Z"
OUTPUT = "Suggested link: paragraph 2 -> claim c1"
ARTIFACTS = {"a_1": {"body": OUTPUT, "hash": sha256_hex(OUTPUT.encode("utf-8"))}}


def _receipt(seal: str, seal_seq: int, note_seq: int | None = None) -> dict:
    r = {"receipt_id": "r_1", "log_id": LOG, "seal_hash": seal, "seal_seq": seal_seq,
         "version": 1, "schema": 1,
         "summary": {"text": "summary", "event_ids": [1, 2]},
         "questions": [{"q": "question", "event_ids": [3], "artifact_ids": ["a_1"]}]}
    if note_seq is not None:
        r["notes"] = [{"text": "drafted on paper in class", "event_ids": [note_seq],
                       "post_seal": True}]
    return r


def _append(store, type, actor="student", payload=None, **kw):
    return store.append(LOG, type=type, actor=actor, payload=payload or {}, ts=TS, **kw)


def _sealed_store() -> tuple[EventStore, str]:
    s = EventStore()
    _append(s, "log.open", "system", {"assignment_id": "as_1", "consent_version": 1,
                                      "mapper_enabled": False})
    _append(s, "source.add", payload={"source_id": "s1", "origin": "teacher",
                                      "url": "https://example.org/a", "title": "Reading — café"})
    _append(s, "editor.batch", payload={"steps": [{"stepType": "replace", "from": 1, "to": 1}],
                                        "input_kind": {"keyboard": 120}}, doc_rev=1)
    _append(s, "map.suggestion", "system", {"suggestion_id": "m1", "artifact_id": "a_1",
                                            "output_hash": ARTIFACTS["a_1"]["hash"]})
    _append(s, "doc.checkpoint", "system", {"doc_rev": 1, "doc_hash": "d" * 64,
                                            "snapshot_ref": "snap_1"})
    submit = _append(s, "submit", payload={"doc_rev": 1, "doc_hash": "d" * 64,
                                           "idempotency_key": "k1"}, doc_rev=1)
    return s, submit["hash"]


@pytest.fixture
def sealed():
    return _sealed_store()


def _complete(store: EventStore, seal: str):
    """Seal, issue the receipt, add a student note. Returns events and receipt."""
    seal_seq = 5
    note = _append(store, "note.add", payload={"span": {"from": 1, "to": 9},
                                               "text": "drafted on paper", "after_release": False})
    receipt = _receipt(seal, seal_seq, note_seq=note["seq"])
    _append(store, "receipt.issued", "system",
            {"receipt_id": "r_1", "receipt_hash": sha256_hex(canonical_json(receipt)),
             "seal_seq": seal_seq, "version": 1})
    return store.events(LOG), receipt


def _bad(events, seal, **kw):
    r = verify(events, seal, **kw)
    assert not r.ok
    return r.problems


# ---- passes ----

def test_clean_log_verifies(sealed):
    store, seal = sealed
    r = verify(store.events(LOG), seal)
    assert r.ok, r.problems
    assert r.seal_seq == 5


@pytest.mark.parametrize("etype", sorted(POST_SEAL_WHITELIST - {"receipt.issued"}))
def test_whitelisted_post_seal_events_verify(sealed, etype):
    store, seal = sealed
    _append(store, etype, payload={"x": 1})
    assert verify(store.events(LOG), seal).ok


def test_full_record_with_receipt_and_artifacts_verifies(sealed):
    store, seal = sealed
    events, receipt = _complete(store, seal)
    r = verify(events, seal, receipt=receipt, artifacts=ARTIFACTS)
    assert r.ok, r.problems


def test_resubmission_window_allows_edits_and_reseals(sealed):
    store, seal1 = sealed
    _append(store, "resubmit.open", "teacher", {"reason": "allowed"})
    _append(store, "editor.batch", payload={"steps": []}, doc_rev=2)
    seal2 = _append(store, "submit", payload={"doc_rev": 2, "doc_hash": "e" * 64,
                                              "idempotency_key": "k2"})["hash"]
    events = store.events(LOG)
    assert verify(events, seal1).ok
    assert verify(events, seal2).ok
    with pytest.raises(SealedError):
        _append(store, "editor.batch", payload={"steps": []})


# ---- the append path ----

def test_append_after_seal_is_refused_for_non_whitelisted(sealed):
    store, _ = sealed
    for etype in ("editor.batch", "card.create", "map.suggestion", "coach.ask"):
        with pytest.raises(SealedError):
            _append(store, etype)
    assert len(store.events(LOG)) == 6


def test_store_refuses_withdrawal_after_the_seal(sealed):
    """D-062 removed withdrawal; the store refuses it like any non-whitelisted event."""
    store, _ = sealed
    assert "record.withdrawn" not in POST_SEAL_WHITELIST
    with pytest.raises(SealedError):
        _append(store, "record.withdrawn", payload={"reason": "changed my mind"})
    assert len(store.events(LOG)) == 6


def test_client_seq_retry_is_deduplicated():
    s = EventStore()
    a = _append(s, "log.open", "system", client_seq=7)
    b = _append(s, "log.open", "system", client_seq=7)
    assert a == b and len(s.events(LOG)) == 1


def test_genesis_and_hash_rule():
    e = build_event(None, LOG, type="log.open", actor="system", payload={}, ts=TS)
    assert e["seq"] == 0
    assert e["prev_hash"] == sha256_hex(("writing-room/" + LOG).encode()) == genesis_prev_hash(LOG)
    body = {k: v for k, v in e.items() if k != "hash"}
    assert e["hash"] == sha256_hex(e["prev_hash"].encode() + canonical_json(body))


def test_canonical_json_rules():
    assert canonical_json({"b": 1, "a": "é"}) == '{"a":"é","b":1}'.encode("utf-8")
    with pytest.raises(CanonicalError):
        canonical_json({"x": 0.5})
    s = EventStore()
    with pytest.raises(CanonicalError):
        _append(s, "log.open", "system", {"ratio": 0.5})
    assert s.events(LOG) == []


# ---- fails: edit, delete, reorder, post-seal ----

@pytest.mark.parametrize("index", range(6))
def test_edit_any_event_fails(sealed, index):
    store, seal = sealed
    events = store.events(LOG)
    events[index]["payload"]["tampered"] = True
    assert any("edited" in p for p in _bad(events, seal))


def test_edit_one_character_in_db_fails(sealed):
    store, seal = sealed
    row = store.db.execute("SELECT body FROM events WHERE seq = 1").fetchone()[0]
    store.db.execute("UPDATE events SET body = ? WHERE seq = 1",
                     (row.replace("café", "cafe"),))
    assert _bad(store.events(LOG), seal)


def test_edit_and_rehash_whole_chain_fails_on_seal(sealed):
    """An editor who recomputes every hash still changes the submit hash, so the seal no longer matches."""
    store, seal = sealed
    events = store.events(LOG)
    events[2]["payload"]["steps"] = []
    prev = genesis_prev_hash(LOG)
    for e in events:
        e["prev_hash"] = prev
        e["hash"] = event_hash(e)
        prev = e["hash"]
    assert verify(events, events[-1]["hash"]).ok  # internally consistent ...
    assert "seal not found in the log" in _bad(events, seal)  # ... but not the sealed record


@pytest.mark.parametrize("index", range(6))
def test_delete_any_event_up_to_seal_fails(sealed, index):
    store, seal = sealed
    store.db.execute("DELETE FROM events WHERE seq = ?", (index,))
    assert _bad(store.events(LOG), seal)


def test_delete_post_seal_event_in_middle_fails(sealed):
    store, seal = sealed
    events, _ = _complete(store, seal)
    del events[6]  # the note, followed by receipt.issued
    assert _bad(events, seal)


@pytest.mark.parametrize("i,j", [(0, 1), (1, 2), (2, 4), (4, 5)])
def test_reorder_two_events_fails(sealed, i, j):
    store, seal = sealed
    events = store.events(LOG)
    events[i], events[j] = events[j], events[i]
    assert _bad(events, seal)


def test_reorder_with_renumbered_seq_fails(sealed):
    store, seal = sealed
    events = store.events(LOG)
    events[1], events[2] = events[2], events[1]
    events[1]["seq"], events[2]["seq"] = 1, 2
    assert _bad(events, seal)


@pytest.mark.parametrize("etype", ["editor.batch", "card.edit", "claim.edit", "map.suggestion",
                                   "coach.ask", "submit"])
def test_non_whitelisted_post_seal_event_fails(sealed, etype):
    """Appended by someone who bypasses the store and computes a valid hash."""
    store, seal = sealed
    events = store.events(LOG)
    events.append(build_event(events[-1], LOG, type=etype, actor="student",
                              payload={"x": 1}, ts=TS))
    assert any("after the seal" in p for p in _bad(events, seal))


def test_seal_must_name_a_submit(sealed):
    store, _ = sealed
    events = store.events(LOG)
    assert any("not a submit" in p for p in _bad(events, events[2]["hash"]))


def test_unknown_seal_fails(sealed):
    store, _ = sealed
    assert _bad(store.events(LOG), "0" * 64)


def test_empty_log_fails():
    assert _bad([], "0" * 64)


def test_other_log_spliced_in_fails(sealed):
    store, seal = sealed
    events = store.events(LOG)
    events[3]["log_id"] = "other"
    assert _bad(events, seal)


# ---- receipt citations and stored outputs ----

def test_changed_receipt_fails(sealed):
    store, seal = sealed
    events, receipt = _complete(store, seal)
    changed = copy.deepcopy(receipt)
    changed["summary"]["text"] = "another summary"
    assert any("receipt_hash" in p for p in _bad(events, seal, receipt=changed,
                                                  artifacts=ARTIFACTS))


def test_receipt_citing_event_after_seal_fails(sealed):
    store, seal = sealed
    events, receipt = _complete(store, seal)
    receipt["summary"]["event_ids"] = [6]
    assert any("after the seal" in p for p in _bad(events, seal, receipt=receipt,
                                                   artifacts=ARTIFACTS))


def test_receipt_citing_missing_event_fails(sealed):
    store, seal = sealed
    events, receipt = _complete(store, seal)
    receipt["summary"]["event_ids"] = [99]
    assert any("not in the log" in p for p in _bad(events, seal, receipt=receipt,
                                                   artifacts=ARTIFACTS))


def test_changed_stored_output_fails(sealed):
    store, seal = sealed
    events, receipt = _complete(store, seal)
    arts = copy.deepcopy(ARTIFACTS)
    arts["a_1"]["body"] = "Another output"
    assert _bad(events, seal, receipt=receipt, artifacts=arts)


def test_missing_stored_output_fails(sealed):
    store, seal = sealed
    events, receipt = _complete(store, seal)
    assert any("not stored" in p for p in _bad(events, seal, receipt=receipt, artifacts={}))


def test_receipt_with_float_cannot_be_hashed(sealed):
    store, seal = sealed
    events, receipt = _complete(store, seal)
    receipt["bands"] = {"by_words": {"untraced": 0.18}}
    assert any("cannot be hashed" in p for p in _bad(events, seal, receipt=receipt,
                                                     artifacts=ARTIFACTS))


# ---- CLI ----

def _cli(tmp_path, events, seal):
    log = tmp_path / "log.jsonl"
    log.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events),
                   encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(SERVER)}
    return subprocess.run([sys.executable, "-m", "engine", "verify", str(log), seal],
                          cwd=SERVER, env=env, capture_output=True, text=True)


def test_cli_verify(tmp_path, sealed):
    store, seal = sealed
    events = store.events(LOG)
    assert _cli(tmp_path, events, seal).returncode == 0
    events[1]["payload"]["title"] = "changed"
    p = _cli(tmp_path, events, seal)
    assert p.returncode == 1 and "edited" in p.stderr
