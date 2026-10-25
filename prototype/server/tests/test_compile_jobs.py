"""Submit-scheduled compile jobs (T-020): receipt v1 with no model call, then the L3e
question upgrade to receipt v2.

Every test uses ROOM_LLM=stub, an injected clock and, where needed, an injected `ask` that
counts calls. No test sleeps and no test contacts a provider.
"""
import json

import pytest
from fastapi.testclient import TestClient

import app.llm as app_llm
from app.compile_jobs import (KIND_COMPILE, KIND_QUESTIONS, RECEIPT_V1, RECEIPT_V2, CompileJobs,
                              compile_key, questions_key)
from app.compile_service import list_alerts
from app.events_service import EventService
from app.main import create_app
from app.receipt_service import llm_ask
from app.receipt_store import ReceiptConflict, ReceiptStore
from engine.events import sha256_hex
from engine.provenance import InMemorySources
from engine.receipt import LLMUnavailable
from engine.receipt.compile import STAMP_KEYS
from engine.receipt.questions import make_artifact
from engine.replay import doc_hash
from tests.test_receipt_compile import BLOCK_TEXT, FIXED_STAMP, LOG, set_doc
from tests.test_receipt_store import build_log
from tests.test_replay_compile import Clock, Writer

BLOCK = "Teachers decide what to ask next about the work"


@pytest.fixture(autouse=True)
def _stub(monkeypatch):
    monkeypatch.setenv("ROOM_LLM", "stub")


def make_sources():
    return InMemorySources(blocks={"b1": BLOCK_TEXT}, helper={})


def make_jobs(svc, *, ask=llm_ask, stamp=FIXED_STAMP, sources_for=None, **kwargs):
    return CompileJobs(svc, sources_for=sources_for or (lambda log_id: make_sources()),
                       ask=ask, stamp=stamp, **kwargs)


def submit_event(svc, log_id=LOG):
    return [e for e in svc.events(log_id) if e["type"] == "submit"][-1]


def issued_events(svc, log_id=LOG):
    return [e for e in svc.events(log_id) if e["type"] == "receipt.issued"]


def jobs_table(jobs):
    return jobs.queue.db.execute(
        "SELECT id, kind, idempotency_key, state, attempts, error_kind FROM jobs ORDER BY id"
    ).fetchall()


def job_id(jobs, kind):
    return next(r[0] for r in jobs_table(jobs) if r[1] == kind)


class FlakyAsk:
    """Answer until the configured call, then report the provider down."""

    def __init__(self, fail_at=2):
        self.calls = 0
        self.fail_at = fail_at
        self.failing = True

    def __call__(self, messages):
        self.calls += 1
        if self.failing and self.calls == self.fail_at:
            raise LLMUnavailable("down")
        return llm_ask(messages)


# ---- a ----------------------------------------------------------------------------------------
def test_provider_down_issues_v1_then_the_questions_job_retries():
    clock = Clock()
    svc = EventService(":memory:", clock)
    calls = []

    def down(messages):
        calls.append(messages)
        raise LLMUnavailable("down")

    jobs = make_jobs(svc, ask=down)
    build_log(svc, clock, LOG)
    seal = submit_event(svc)["hash"]

    # The compile job exists as soon as submit returns (it was enqueued in that transaction).
    rows = jobs_table(jobs)
    assert [(r[1], r[2], r[3]) for r in rows] == [
        (KIND_COMPILE, compile_key(LOG, seal), "queued")]

    jobs.run_until_idle()
    v1 = jobs.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V1)
    assert v1 is not None
    assert v1.receipt["status"] == "questions_pending"
    assert v1.receipt["questions_pending"] is True
    assert v1.receipt["questions"]
    assert all(q["q"] is None and q["pillar"] is None and q["grounding"] == []
               for q in v1.receipt["questions"])
    assert [e["payload"]["version"] for e in issued_events(svc)] == [RECEIPT_V1]

    questions_job = jobs.queue.get(job_id(jobs, KIND_QUESTIONS))
    assert questions_job.state == "queued"  # retryable, waiting on the schedule
    assert questions_job.attempts == 1 and questions_job.error_kind == "llm_unavailable"
    assert calls  # the question path did try the provider
    assert jobs.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V2) is None
    assert svc.verify(LOG)["ok"]


# ---- b ----------------------------------------------------------------------------------------
def test_queued_work_survives_a_restart(tmp_path):
    path = str(tmp_path / "room.db")
    clock = Clock()
    svc = EventService(path, clock)
    calls = []

    def ask(messages):
        calls.append(messages)
        return llm_ask(messages)

    first = make_jobs(svc, ask=ask)
    build_log(svc, clock, LOG)
    seal = submit_event(svc)["hash"]
    assert jobs_table(first)
    svc.close()

    again = EventService(path, clock)
    jobs = make_jobs(again, ask=ask)
    assert jobs.reconcile() == 0  # the compile job crossed the restart
    jobs.run_until_idle()

    assert jobs.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V1) is not None
    assert jobs.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V2) is not None
    assert calls
    assert again.verify(LOG)["ok"]
    again.close()


# ---- c ----------------------------------------------------------------------------------------
def test_no_duplicate_issuance_across_retry_and_lease_recovery():
    clock = Clock()
    svc = EventService(":memory:", clock)
    jobs = make_jobs(svc)
    build_log(svc, clock, LOG)
    seal = submit_event(svc)["hash"]

    # A submit retried with the same idempotency key schedules nothing new.
    replay = svc.submit(LOG, idempotency_key="k1", doc_rev=0, doc_hash="0" * 64,
                        snapshot={}, lease_token="unused")
    assert replay["replayed"] is True
    assert len([r for r in jobs_table(jobs) if r[2] == compile_key(LOG, seal)]) == 1

    # A lease expiry makes the compile run twice; the second run publishes once.
    first = jobs.queue.claim(worker_id="worker-a")
    assert first.kind == KIND_COMPILE and first.attempts == 1
    clock.advance(seconds=301)
    second = jobs.queue.claim(worker_id="worker-b")
    assert second.id == first.id and second.attempts == 2
    compile_result = jobs.handle_compile(second)
    jobs.queue.complete(second, compile_result)
    v1 = jobs.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V1)
    assert v1 is not None

    # The same for the question upgrade.
    q_first = jobs.queue.claim(worker_id="worker-a")
    assert q_first.kind == KIND_QUESTIONS
    clock.advance(seconds=301)
    q_second = jobs.queue.claim(worker_id="worker-b")
    assert q_second.id == q_first.id and q_second.attempts == 2
    questions_result = jobs.handle_questions(q_second)
    jobs.queue.complete(q_second, questions_result)
    v2 = jobs.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V2)
    assert v2 is not None
    before = (v1.body, v2.body, v1.receipt_hash, v2.receipt_hash)

    # Re-running each handler for the same job changes no bytes and writes no event.
    assert jobs.handle_compile(second) == compile_result
    assert jobs.handle_questions(q_second) == questions_result
    v1_after = jobs.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V1)
    v2_after = jobs.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V2)
    assert (v1_after.body, v2_after.body, v1_after.receipt_hash,
            v2_after.receipt_hash) == before
    versions = [e["payload"]["version"] for e in issued_events(svc)]
    assert versions.count(RECEIPT_V1) == 1 and versions.count(RECEIPT_V2) == 1
    assert svc.verify(LOG)["ok"]


# ---- d ----------------------------------------------------------------------------------------
def test_stored_outputs_are_reused_and_a_finished_upgrade_asks_nothing():
    clock = Clock()
    svc = EventService(":memory:", clock)
    ask = FlakyAsk(fail_at=2)
    jobs = make_jobs(svc, ask=ask)
    build_log(svc, clock, LOG)
    seal = submit_event(svc)["hash"]

    jobs.run_until_idle()  # compile, then the first question attempt
    v1 = jobs.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V1)
    total_questions = len(v1.receipt["questions"])
    assert total_questions > 1
    stored = jobs.receipts.stored_artifacts(LOG)
    assert len(stored) == 1  # the answer obtained before the outage
    assert ask.calls == 2  # one answer, one outage; later questions are skipped
    assert jobs.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V2) is None

    ask.failing = False
    clock.advance(minutes=1)
    before_retry = ask.calls
    jobs.run_until_idle()
    retry_calls = ask.calls - before_retry
    assert retry_calls == total_questions - len(stored)  # the answered one is not asked again

    v2 = jobs.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V2)
    assert v2 is not None and v2.receipt["status"] == "complete"
    before = ask.calls
    jobs.handle_questions(jobs.queue.get(job_id(jobs, KIND_QUESTIONS)))
    assert ask.calls == before  # a finished upgrade makes no model call


# ---- e ----------------------------------------------------------------------------------------
def test_l1_fallback_is_upgraded_and_v1_is_unchanged():
    clock = Clock()
    svc = EventService(":memory:", clock)
    jobs = make_jobs(svc)
    build_log(svc, clock, LOG)
    seal = submit_event(svc)["hash"]

    jobs.run_until_idle(max_jobs=1)  # compile only
    v1 = jobs.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V1)
    assert v1.receipt["status"] == "questions_pending"
    v1_body, v1_hash = v1.body, v1.receipt_hash
    assert jobs.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V2) is None

    jobs.run_until_idle()
    v2 = jobs.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V2)
    assert v2.receipt["status"] == "complete"
    assert all(q["q"] for q in v2.receipt["questions"])

    v1_after = jobs.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V1)
    assert v1_after.body == v1_body and v1_after.receipt_hash == v1_hash
    assert jobs.receipts.verify(LOG, version=RECEIPT_V1).ok
    assert jobs.receipts.verify(LOG, version=RECEIPT_V2).ok
    assert jobs.receipts.latest(LOG).version == RECEIPT_V2
    assert svc.verify(LOG)["ok"]


# ---- f ----------------------------------------------------------------------------------------
def test_retries_stop_after_five_tries_and_keep_v1():
    clock = Clock()
    svc = EventService(":memory:", clock)

    def down(messages):
        raise LLMUnavailable("down")

    jobs = make_jobs(svc, ask=down)
    build_log(svc, clock, LOG)
    seal = submit_event(svc)["hash"]

    jobs.run_until_idle()  # compile, then question attempt 1
    for delay in (1, 4, 16, 16):
        clock.advance(minutes=delay)
        jobs.run_until_idle()

    qid = job_id(jobs, KIND_QUESTIONS)
    questions_job = jobs.queue.get(qid)
    assert questions_job.state == "failed"
    assert questions_job.attempts == 5
    assert questions_job.error_kind == "llm_unavailable"

    alerts = list_alerts(svc, LOG)
    assert [a["kind"] for a in alerts] == ["questions_failed"]
    assert alerts[0]["detail"]["job_kind"] == KIND_QUESTIONS
    assert alerts[0]["detail"]["attempts"] == 5

    latest = jobs.receipts.latest(LOG)
    assert latest.version == RECEIPT_V1
    assert latest.receipt["status"] == "questions_pending"
    assert jobs.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V2) is None

    assert jobs.reconcile() == 0
    assert jobs.queue.get(qid).state == "failed"  # a terminal job is not requeued
    assert jobs.queue.get(qid).attempts == 5


def test_lease_recovery_does_not_use_up_a_question_try():
    clock = Clock()
    svc = EventService(":memory:", clock)

    def down(messages):
        raise LLMUnavailable("down")

    jobs = make_jobs(svc, ask=down)
    build_log(svc, clock, LOG)
    seal = submit_event(svc)["hash"]

    jobs.run_until_idle()  # compile, then question attempt 1 (retryable failure 1)
    qid = job_id(jobs, KIND_QUESTIONS)
    assert jobs.queue.get(qid).state == "queued"
    assert jobs.queue.get(qid).retry_failures == 1

    # Wait out the 1-minute backoff, claim the queued job, then let its lease expire.
    clock.advance(minutes=1)
    claimed = jobs.queue.claim(worker_id="worker-a")
    assert claimed.id == qid
    assert claimed.attempts == 2 and claimed.retry_failures == 1
    clock.advance(seconds=301)
    assert jobs.queue.recover_expired() == 1
    recovered = jobs.queue.get(qid)
    assert recovered.state == "queued"
    assert recovered.retry_failures == 1  # lease recovery is not a try (D-054)

    jobs.run_until_idle()  # retryable failure 2
    assert jobs.queue.get(qid).state == "queued"
    clock.advance(minutes=4)
    jobs.run_until_idle()  # retryable failure 3
    clock.advance(minutes=16)
    jobs.run_until_idle()  # retryable failure 4
    after_four = jobs.queue.get(qid)
    assert after_four.state == "queued"
    assert after_four.retry_failures == 4

    clock.advance(minutes=16)
    jobs.run_until_idle()  # retryable failure 5 -> terminal
    questions_job = jobs.queue.get(qid)
    assert questions_job.state == "failed"
    assert questions_job.retry_failures == 5
    assert questions_job.error_kind == "llm_unavailable"

    alerts = list_alerts(svc, LOG)
    assert [a["kind"] for a in alerts] == ["questions_failed"]
    assert alerts[0]["detail"]["retry_failures"] == 5
    assert alerts[0]["detail"]["job_kind"] == KIND_QUESTIONS

    latest = jobs.receipts.latest(LOG)
    assert latest.version == RECEIPT_V1
    assert latest.receipt["status"] == "questions_pending"
    assert jobs.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V2) is None


# ---- g ----------------------------------------------------------------------------------------
def test_replay_mismatch_still_issues_v1_and_alerts():
    clock = Clock()
    svc = EventService(":memory:", clock)
    jobs = make_jobs(svc, sources_for=lambda log_id: InMemorySources(blocks={"b1": BLOCK}))
    w = Writer(svc, clock, LOG)
    w.insert("Hello world")
    w.checkpoint()
    w.insert(" quoted", "quote", "b1")
    w.checkpoint(hash=sha256_hex(b"something else"))
    w.insert(" more")
    w.checkpoint()
    w.submit()

    jobs.run_until_idle()
    seal = submit_event(svc)["hash"]
    v1 = jobs.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V1)
    assert v1.receipt["status"] == "replay_mismatch"
    assert v1.receipt["built_from"] == "browser_copy"
    assert v1.receipt["replay_note"]

    alerts = [a for a in list_alerts(svc, LOG) if a["kind"] == "replay_mismatch"]
    assert len(alerts) == 1
    assert alerts[0]["detail"]["reason"] == "hash_mismatch"
    assert "Hello" not in json.dumps(alerts[0])  # never student text

    engine = v1.receipt["engine"]
    assert set(STAMP_KEYS) <= set(engine)
    assert engine["flags"]["l3b"] is False
    assert svc.verify(LOG)["ok"]


# ---- h ----------------------------------------------------------------------------------------
def test_a_seal_without_scheduling_is_recovered_and_issues_once():
    clock = Clock()
    svc = EventService(":memory:", clock)
    build_log(svc, clock, LOG)

    jobs = make_jobs(svc)
    assert jobs.reconcile() == 1  # exactly one compile job for the one submit
    jobs.run_until_idle(max_jobs=1)
    assert [e["payload"]["version"] for e in issued_events(svc)] == [RECEIPT_V1]


def test_a_retried_submit_after_such_a_crash_schedules_once():
    clock = Clock()
    svc = EventService(":memory:", clock)
    build_log(svc, clock, LOG)
    seal = submit_event(svc)["hash"]

    jobs = make_jobs(svc)
    replay = svc.submit(LOG, idempotency_key="k1", doc_rev=0, doc_hash="0" * 64,
                        snapshot={}, lease_token="unused")
    assert replay["replayed"] is True
    assert len([r for r in jobs_table(jobs) if r[2] == compile_key(LOG, seal)]) == 1
    assert jobs.reconcile() == 0


def test_a_failing_seal_hook_rolls_the_submit_back():
    clock = Clock()
    svc = EventService(":memory:", clock)
    state = {"fail": True}

    def hook(log_id, event, db):
        if state["fail"]:
            raise RuntimeError("scheduling failed")

    svc.add_seal_hook(hook)
    w = Writer(svc, clock, LOG)
    w.insert("Hello world")
    w.checkpoint()
    with pytest.raises(RuntimeError):
        w.submit()
    assert not [e for e in svc.events(LOG) if e["type"] == "submit"]

    state["fail"] = False
    result = w.submit()
    assert result["seal"]
    assert [e for e in svc.events(LOG) if e["type"] == "submit"]
    assert svc.verify(LOG)["ok"]


# ---- i ----------------------------------------------------------------------------------------
def test_no_write_transaction_is_open_during_a_model_call():
    clock = Clock()
    svc = EventService(":memory:", clock)
    states = []

    def ask(messages):
        states.append(svc.db.in_transaction)
        return llm_ask(messages)

    jobs = make_jobs(svc, ask=ask)
    build_log(svc, clock, LOG)
    jobs.run_until_idle()
    assert states
    assert not any(states)


# ---- j ----------------------------------------------------------------------------------------
def _claimed_log(svc, clock, log_id=LOG):
    """A sealed log with one claim, so the question upgrade has a candidate."""
    w = Writer(svc, clock, log_id)
    svc.append_event(log_id, type="source.add", actor="teacher",
                     payload={"source_id": "s1", "origin": "teacher", "title": "A study",
                              "url": None})
    svc.append_event(log_id, type="claim.create", actor="student",
                     payload={"claim_id": "k1", "text": "A claim worth examining",
                              "card_ids": [], "parent_claim_id": None})
    set_doc(w, [("A sentence with a claim.", ["k1"], "typed", None)])
    w.checkpoint()
    return w


def test_resubmission_gets_its_own_jobs_and_receipts():
    clock = Clock()
    svc = EventService(":memory:", clock)
    jobs = make_jobs(svc)
    w = _claimed_log(svc, clock)
    first = w.submit("k1")
    first_hash = first["seal"]

    jobs.run_until_idle()
    first_v1 = jobs.receipts.get(LOG, seal_hash=first_hash, version=RECEIPT_V1)
    first_v2 = jobs.receipts.get(LOG, seal_hash=first_hash, version=RECEIPT_V2)
    assert first_v1 is not None and first_v2 is not None
    first_bytes = (first_v1.body, first_v2.body)

    svc.open_resubmission(LOG, reason="revise")
    w.insert(" and a second part")
    w.checkpoint()
    second = w.submit("k2")
    second_hash = second["seal"]
    assert second_hash != first_hash

    keys = {r[2] for r in jobs_table(jobs)}
    assert {compile_key(LOG, first_hash), compile_key(LOG, second_hash)} <= keys

    jobs.run_until_idle()
    assert jobs.receipts.get(LOG, seal_hash=second_hash, version=RECEIPT_V1) is not None
    assert jobs.receipts.get(LOG, seal_hash=second_hash, version=RECEIPT_V2) is not None
    now_first_v1 = jobs.receipts.get(LOG, seal_hash=first_hash, version=RECEIPT_V1)
    now_first_v2 = jobs.receipts.get(LOG, seal_hash=first_hash, version=RECEIPT_V2)
    assert (now_first_v1.body, now_first_v2.body) == first_bytes
    assert svc.verify(LOG)["ok"]


# ---- k ----------------------------------------------------------------------------------------
def test_http_submit_schedules_a_compile_job_on_the_shared_lock():
    clock = Clock()
    app = create_app(":memory:", clock, sources_for=lambda log_id: make_sources(),
                     start_job_loop=False)
    with TestClient(app) as client:
        svc = app.state.events
        w = Writer(svc, clock, LOG)
        w.insert("Hello world")
        w.checkpoint()
        clock.advance(minutes=6)
        body = {"idempotency_key": "http-key-1", "doc_rev": w.rev,
                "doc_hash": doc_hash(w.doc), "snapshot": w.doc.to_json(),
                "lease_token": w.token()}
        response = client.post(f"/logs/{LOG}/submit", json=body)
        assert response.status_code == 200, response.text
        seal = response.json()["seal"]

        jobs = app.state.jobs
        assert jobs.queue._lock is svc._lock
        rows = jobs.queue.db.execute(
            "SELECT kind, idempotency_key, state FROM jobs").fetchall()
        assert (KIND_COMPILE, compile_key(LOG, seal), "queued") in rows


# ---- l ----------------------------------------------------------------------------------------
def test_a_non_retryable_compile_failure_writes_a_compile_failed_alert():
    clock = Clock()
    svc = EventService(":memory:", clock)

    def boom(log_id):
        raise RuntimeError("sources unavailable")

    jobs = make_jobs(svc, sources_for=boom)
    build_log(svc, clock, LOG)
    jobs.run_until_idle()

    compile_job = jobs.queue.get(job_id(jobs, KIND_COMPILE))
    assert compile_job.state == "failed"
    assert compile_job.error_kind == "RuntimeError"
    assert compile_job.attempts == 1
    assert not [r for r in jobs_table(jobs) if r[1] == KIND_QUESTIONS]

    alerts = list_alerts(svc, LOG)
    assert [a["kind"] for a in alerts] == ["compile_failed"]
    detail = alerts[0]["detail"]
    assert detail["job_kind"] == KIND_COMPILE
    assert detail["error_kind"] == "RuntimeError"
    assert detail["attempts"] == 1
    assert "unavailable" not in json.dumps(detail)  # never exception messages


# ---- reconcile paths: startup, pending questions and lease recovery --------------------------
def test_startup_reconcile_schedules_a_seal_committed_without_a_job(tmp_path, monkeypatch):
    path = str(tmp_path / "room.db")
    clock = Clock()
    svc = EventService(path, clock)  # deliberately no CompileJobs attached
    build_log(svc, clock, LOG)
    seal = submit_event(svc)["hash"]
    svc.close()

    # The lifespan pings providers; keep it off the network even outside stub mode.
    monkeypatch.setattr(app_llm, "ping_backends", lambda: [])
    app = create_app(path, clock, sources_for=lambda log_id: make_sources(),
                     start_job_loop=False)
    assert not [r for r in jobs_table(app.state.jobs) if r[1] == KIND_COMPILE]

    with TestClient(app):  # runs the lifespan, which reconciles
        rows = [r for r in jobs_table(app.state.jobs) if r[1] == KIND_COMPILE]
        assert [(r[2], r[3]) for r in rows] == [(compile_key(LOG, seal), "queued")]


def test_reconcile_schedules_questions_for_a_pending_v1_without_v2():
    clock = Clock()
    svc = EventService(":memory:", clock)
    jobs = make_jobs(svc)
    build_log(svc, clock, LOG)
    seal = submit_event(svc)["hash"]

    jobs.run_until_idle(max_jobs=1)  # issue v1; its questions job is queued but not run
    v1 = jobs.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V1)
    assert v1 is not None and v1.receipt["questions_pending"] is True
    assert jobs.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V2) is None

    # Simulate a crash after v1 was issued but before the questions job survived.
    jobs.queue.db.execute("DELETE FROM jobs WHERE kind = ?", (KIND_QUESTIONS,))
    assert not [r for r in jobs_table(jobs) if r[1] == KIND_QUESTIONS]

    assert jobs.reconcile() == 1
    rows = [r for r in jobs_table(jobs) if r[1] == KIND_QUESTIONS]
    assert [(r[2], r[3]) for r in rows] == [(questions_key(LOG, seal), "queued")]
    assert jobs.reconcile() == 0
    assert len([r for r in jobs_table(jobs) if r[1] == KIND_QUESTIONS]) == 1

    # Once v2 is stored, the same missing row is not recreated.
    jobs.run_until_idle()
    assert jobs.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V2) is not None
    jobs.queue.db.execute("DELETE FROM jobs WHERE kind = ?", (KIND_QUESTIONS,))
    assert jobs.reconcile() == 0
    assert not [r for r in jobs_table(jobs) if r[1] == KIND_QUESTIONS]


def test_reconcile_recovers_an_expired_lease():
    clock = Clock()
    svc = EventService(":memory:", clock)
    jobs = make_jobs(svc)
    build_log(svc, clock, LOG)

    claimed = jobs.queue.claim(worker_id="worker-a")
    assert claimed.kind == KIND_COMPILE and claimed.lease_token is not None

    clock.advance(seconds=301)
    assert jobs.reconcile() == 0
    # Do not claim again: claim() recovers expired leases itself and would mask this.
    recovered = jobs.queue.get(claimed.id)
    assert recovered.state == "queued"
    assert recovered.lease_token is None


# ---- artifact storage helper ------------------------------------------------------------------
def test_store_artifacts_in_tx_inserts_skips_and_rejects_conflicts():
    svc = EventService(":memory:")
    store = ReceiptStore(svc.db)
    artifact = make_artifact("receipt_question", "p" * 64, '{"question":"x"}')
    aid = artifact["artifact_id"]
    body = '{"question":"y"}'
    changed = {"artifact_id": aid, "task": artifact["task"],
               "prompt_hash": artifact["prompt_hash"], "body": body,
               "hash": sha256_hex(body.encode())}

    with svc._lock, svc._tx():
        assert store.store_artifacts_in_tx(LOG, {aid: artifact}) == 1
        assert store.store_artifacts_in_tx(LOG, {aid: artifact}) == 0
        with pytest.raises(ReceiptConflict):
            store.store_artifacts_in_tx(LOG, {aid: changed})

    assert store.artifacts(LOG) == {aid: artifact}
    svc.close()
