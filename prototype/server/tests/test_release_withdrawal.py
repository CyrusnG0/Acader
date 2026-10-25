"""Release boundaries and transactional withdrawal (T-021; receipt.md §7, D10).

Every test uses ROOM_LLM=stub, an injected clock and in-memory SQLite. No test sleeps and no
test contacts a provider. The identities below are synthetic constructor arguments; they are
not an authentication layer.
"""
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.compile_jobs import (KIND_COMPILE, KIND_QUESTIONS, RECEIPT_V1, RECEIPT_V2,
                              CompileJobs)
from app.compile_service import list_alerts
from app.events_service import EventService
from app.jobs import JobQueue, JobRunner, LeaseLost
from app.lifecycle import (AccessDenied, AfterRelease, Identity, PHASE_BASE, PHASE_CAP,
                           RecordScope, ReceiptLifecycle, release_key)
from app.main import create_app
from app.receipt_service import llm_ask
from app.withdrawal import RecordWithdrawn
from engine.receipt import LLMUnavailable
from tests.test_receipt_compile import FIXED_STAMP
from tests.test_receipt_store import build_log
from tests.test_replay_compile import Clock

LOG = "L1"
LOG2 = "L2"
TENANT = "tenant-1"
OWNER = "student-1"
TEACHER = Identity(TENANT, "teacher")
STUDENT = Identity(TENANT, "student", OWNER)
STUDENT_OTHER = Identity(TENANT, "student", "student-2")
TENANT2_TEACHER = Identity("tenant-2", "teacher")
TENANT2_STUDENT = Identity("tenant-2", "student", "student-2")


@pytest.fixture(autouse=True)
def _stub(monkeypatch):
    monkeypatch.setenv("ROOM_LLM", "stub")


def make_sources():
    from engine.provenance import InMemorySources
    from tests.test_receipt_compile import BLOCK_TEXT
    return InMemorySources(blocks={"b1": BLOCK_TEXT}, helper={})


class Providers:
    """Per-log deadline and scope supplied by the caller (a stand-in for the roster layer)."""

    def __init__(self, deadlines=None, scopes=None):
        self.deadlines = dict(deadlines or {})
        self.scopes = dict(scopes or {})

    def deadline_for(self, log_id):
        return self.deadlines.get(log_id)

    def scope_for(self, log_id):
        return self.scopes.get(log_id, RecordScope(TENANT, OWNER))


class Down:
    def __init__(self):
        self.up = False

    def __call__(self, messages):
        if not self.up:
            raise LLMUnavailable("down")
        return llm_ask(messages)


def make_system(clock, *, deadlines=None, scopes=None, ask=None):
    svc = EventService(":memory:", clock)
    jobs = CompileJobs(svc, sources_for=lambda log_id: make_sources(),
                       ask=ask or llm_ask, stamp=FIXED_STAMP)
    providers = Providers(deadlines, scopes)
    lifecycle = ReceiptLifecycle(svc, queue=jobs.queue, receipts=jobs.receipts,
                                 deadline_for=providers.deadline_for,
                                 scope_for=providers.scope_for)
    jobs.add_questions_hook(lifecycle.questions_ready)
    return svc, jobs, lifecycle, providers


def submit_event(svc, log_id=LOG):
    return [e for e in svc.events(log_id) if e["type"] == "submit"][-1]


def parse(ts):
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def record(lifecycle, log_id=LOG, seal=None):
    seal = seal or submit_event(lifecycle.service, log_id)["hash"]
    return lifecycle._release_row(log_id, seal)


def release_job(jobs, lifecycle, phase, log_id=LOG):
    seal = submit_event(lifecycle.service, log_id)["hash"]
    row = jobs.queue.db.execute(
        "SELECT id FROM jobs WHERE idempotency_key = ?",
        (release_key(log_id, seal, phase),)).fetchone()
    assert row is not None
    return jobs.queue.get(row[0])


def runner(jobs, lifecycle):
    return JobRunner(jobs.queue, {**jobs.handlers(), **lifecycle.handlers()},
                     worker_id="t021")


def issued_versions(svc, log_id=LOG):
    return [e["payload"]["version"] for e in svc.events(log_id)
            if e["type"] == "receipt.issued"]


def job_states(jobs):
    return {r[1]: r[0] for r in jobs.queue.db.execute(
        "SELECT state, kind FROM jobs ORDER BY id")}


def test_deadline_later_than_24h_sets_base_and_release_waits_for_it():
    clock = Clock()
    deadline = parse("2026-11-06T12:00:00Z")
    svc, jobs, lifecycle, _ = make_system(clock, deadlines={LOG: deadline})
    build_log(svc, clock, LOG)
    jobs.run_until_idle()  # receipt v2, questions ready

    rec = record(lifecycle)
    assert parse(rec["base_at"]) == deadline  # deadline dominates submit + 24 h
    base_job = release_job(jobs, lifecycle, PHASE_BASE)

    clock.t = deadline - timedelta(seconds=1)
    assert lifecycle.handle_release(base_job) == {"status": "waiting"}
    assert record(lifecycle)["released_at"] is None

    clock.t = deadline
    result = lifecycle.handle_release(base_job)
    assert result == {"status": "released", "released_at": "2026-11-06T12:00:00Z",
                      "released_version": RECEIPT_V2, "release_kind": "ready"}
    assert record(lifecycle)["released_version"] == RECEIPT_V2


def test_submit_plus_24h_sets_base_when_deadline_is_earlier():
    clock = Clock()
    svc, jobs, lifecycle, _ = make_system(clock, deadlines={LOG: parse("2026-11-01T00:00:00Z")})
    build_log(svc, clock, LOG)
    jobs.run_until_idle()

    base = parse(record(lifecycle)["base_at"])
    assert base == parse(submit_event(svc)["ts"]) + timedelta(hours=24)
    base_job = release_job(jobs, lifecycle, PHASE_BASE)

    clock.t = base - timedelta(seconds=1)
    assert lifecycle.handle_release(base_job)["status"] == "waiting"
    assert record(lifecycle)["released_at"] is None

    clock.t = base
    result = lifecycle.handle_release(base_job)
    assert result["status"] == "released" and result["release_kind"] == "ready"


def test_cap_releases_pending_questions_once_and_alerts_an_operator():
    clock = Clock()
    down = Down()
    svc, jobs, lifecycle, _ = make_system(clock, ask=down)
    build_log(svc, clock, LOG)
    jobs.run_until_idle(max_jobs=1)  # v1 only; questions stay pending

    rec = record(lifecycle)
    base, cap = parse(rec["base_at"]), parse(rec["cap_at"])
    assert cap - base == timedelta(hours=48)  # the cap is exactly 48 h after the base
    base_job = release_job(jobs, lifecycle, PHASE_BASE)
    cap_job = release_job(jobs, lifecycle, PHASE_CAP)

    clock.t = base
    assert lifecycle.handle_release(base_job)["status"] == "waiting"
    clock.t = cap - timedelta(seconds=1)
    assert lifecycle.handle_release(cap_job)["status"] == "waiting"
    assert record(lifecycle)["released_at"] is None

    clock.t = cap
    result = lifecycle.handle_release(cap_job)
    assert result == {"status": "released", "released_at": rec["cap_at"],
                      "released_version": RECEIPT_V1, "release_kind": "cap"}
    released = lifecycle.receipts.get(LOG, seal_hash=rec["seal_hash"], version=RECEIPT_V1)
    assert released.receipt["questions_pending"] is True

    alerts = [a for a in list_alerts(svc, LOG) if a["kind"] == "release_cap"]
    assert len(alerts) == 1
    assert alerts[0]["detail"]["version"] == RECEIPT_V1
    assert alerts[0]["detail"]["questions_pending"] is True
    assert "Fluid" not in str(alerts[0])  # identifiers and flags only, never student text


def test_cap_with_no_receipt_alerts_and_never_invents_one():
    clock = Clock()
    svc, jobs, lifecycle, _ = make_system(clock)
    build_log(svc, clock, LOG)  # sealed, but the compile job was never run
    rec = record(lifecycle)
    clock.t = parse(rec["cap_at"])

    result = lifecycle.handle_release(release_job(jobs, lifecycle, PHASE_CAP))

    assert result == {"status": "no_receipt"}
    assert record(lifecycle)["released_at"] is None
    assert lifecycle._latest_receipt(LOG, rec["seal_hash"]) is None
    alerts = [a for a in list_alerts(svc, LOG) if a["kind"] == "release_no_receipt"]
    assert len(alerts) == 1
    assert alerts[0]["detail"]["doc_rev"] == rec["doc_rev"]


def test_duplicate_release_does_not_change_state_alerts_or_events():
    clock = Clock()
    svc, jobs, lifecycle, _ = make_system(clock)
    build_log(svc, clock, LOG)
    jobs.run_until_idle()
    events_before = len(svc.events(LOG))
    base_job = release_job(jobs, lifecycle, PHASE_BASE)
    cap_job = release_job(jobs, lifecycle, PHASE_CAP)

    clock.t = parse(record(lifecycle)["base_at"])
    first = lifecycle.handle_release(base_job)
    assert first["status"] == "released"
    released_at = record(lifecycle)["released_at"]

    assert lifecycle.handle_release(base_job) == first
    clock.t = parse(record(lifecycle)["cap_at"])
    assert lifecycle.handle_release(cap_job) == first
    assert record(lifecycle)["released_at"] == released_at
    assert len(svc.events(LOG)) == events_before
    assert [a for a in list_alerts(svc, LOG) if a["kind"] == "release_cap"] == []
    assert issued_versions(svc) == [RECEIPT_V1, RECEIPT_V2]


def test_no_teacher_receipt_contents_before_release():
    clock = Clock()
    svc, jobs, lifecycle, _ = make_system(clock, deadlines={LOG: parse("2026-11-10T00:00:00Z")})
    build_log(svc, clock, LOG)
    jobs.run_until_idle()  # questions ready, but base is still days away

    view = lifecycle.teacher_view(TEACHER, LOG)
    assert set(view) == {"status", "ready_by"}
    assert view["status"] == "compiling"
    assert view["ready_by"] == record(lifecycle)["cap_at"]
    assert "receipt" not in view and "summary" not in view and "questions" not in view

    clock.t = parse(record(lifecycle)["base_at"])
    lifecycle.handle_release(release_job(jobs, lifecycle, PHASE_BASE))
    after = lifecycle.teacher_view(TEACHER, LOG)
    assert after["status"] == "ready"
    assert after["receipt"]["version"] == RECEIPT_V2
    assert "bands" in after["receipt"]


def test_outage_then_questions_arrive_before_cap_and_release_early():
    clock = Clock()
    down = Down()
    svc, jobs, lifecycle, _ = make_system(clock, ask=down)
    build_log(svc, clock, LOG)
    jobs.run_until_idle(max_jobs=1)  # v1, then the questions attempt fails

    base = parse(record(lifecycle)["base_at"])
    clock.t = base
    assert lifecycle.handle_release(release_job(jobs, lifecycle, PHASE_BASE))["status"] == \
        "waiting"

    down.up = True  # the provider returns long before the cap
    runner(jobs, lifecycle).run_until_idle()

    rec = record(lifecycle)
    assert rec["released_at"] == rec["base_at"]  # released as soon as questions were ready
    assert rec["release_kind"] == "ready"
    assert rec["released_version"] == RECEIPT_V2
    assert [a for a in list_alerts(svc, LOG) if a["kind"] == "release_cap"] == []


def test_outage_through_cap_late_questions_are_marked_added_after_release():
    clock = Clock()
    down = Down()
    svc, jobs, lifecycle, _ = make_system(clock, ask=down)
    build_log(svc, clock, LOG)
    jobs.run_until_idle(max_jobs=1)  # v1 pending, questions job queued

    cap = parse(record(lifecycle)["cap_at"])
    clock.t = cap
    assert lifecycle.handle_release(release_job(jobs, lifecycle, PHASE_CAP))["status"] == \
        "released"
    v1 = lifecycle.receipts.get(LOG, seal_hash=record(lifecycle)["seal_hash"],
                                version=RECEIPT_V1)
    v1_body = v1.body

    # A slow question attempt finishes after the cap; it is stored, never folded into v1.
    down.up = True
    questions_job = jobs.queue.get(jobs.queue.db.execute(
        "SELECT id FROM jobs WHERE kind = ?", (KIND_QUESTIONS,)).fetchone()[0])
    jobs.handle_questions(questions_job)

    v1_after = lifecycle.receipts.get(LOG, seal_hash=record(lifecycle)["seal_hash"],
                                     version=RECEIPT_V1)
    assert v1_after.body == v1_body
    view = lifecycle.teacher_view(TEACHER, LOG)
    assert view["receipt"]["version"] == RECEIPT_V1
    assert view["late_questions"]
    assert all(q["added_after_release"] is True and q["q"] for q in view["late_questions"])
    assert view["status"] == "ready"


def test_a_failed_release_job_alerts_as_release_not_questions():
    clock = Clock()
    svc, jobs, lifecycle, _ = make_system(clock)
    build_log(svc, clock, LOG)
    jobs.run_until_idle()
    clock.t = parse(record(lifecycle)["base_at"])
    claimed = jobs.queue.claim(worker_id="worker-release")
    assert claimed.kind == "receipt.release" and claimed.id == \
        release_job(jobs, lifecycle, PHASE_BASE).id

    jobs.queue.fail(claimed, error_kind="database", retryable=False)

    alerts = [a for a in list_alerts(svc, LOG) if a["kind"] == "release_failed"]
    assert len(alerts) == 1
    assert alerts[0]["detail"]["job_kind"] == "receipt.release"
    assert [a for a in list_alerts(svc, LOG) if a["kind"] == "questions_failed"] == []


def test_lifecycle_refuses_a_queue_that_does_not_share_the_event_lock():
    svc = EventService(":memory:", Clock())
    with pytest.raises(ValueError):
        ReceiptLifecycle(svc, queue=JobQueue(svc.db))
    svc.close()


# ---------------------------------------------------------------- withdrawal
def test_withdrawal_cancels_work_deletes_unreleased_outputs_and_keeps_submitted_work():
    clock = Clock()
    svc, jobs, lifecycle, _ = make_system(clock)
    build_log(svc, clock, LOG)
    jobs.run_until_idle(max_jobs=1)  # v1 stored, questions queued
    seal = submit_event(svc)["hash"]
    assert lifecycle.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V1) is not None

    result = lifecycle.withdraw(STUDENT, LOG, reason="changed my mind")
    assert result["status"] == "record_removed" and result["replayed"] is False
    assert result["event"]["type"] == "record.withdrawn"
    assert result["event"]["payload"] == {"reason": "changed my mind"}

    assert lifecycle.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V1) is None
    assert lifecycle.receipts.artifacts(LOG) == {}
    assert not ({r[0] for r in jobs.queue.db.execute(
        "SELECT state FROM jobs")} & {"queued", "running"})
    tomb = lifecycle._tombstone(LOG)
    assert tomb is not None and tomb["withdrawn_at"] == result["withdrawn_at"]
    assert all(r[0] is not None for r in svc.db.execute(
        "SELECT withdrawn_at FROM release_records WHERE log_id = ?", (LOG,)))
    # Submitted work stays submitted, and the withdrawal is a whitelisted post-seal event.
    assert [e["type"] for e in svc.events(LOG)].count("submit") == 1
    assert svc.verify(LOG)["ok"] is True
    assert lifecycle.teacher_view(TEACHER, LOG) == {
        "status": "record_removed", "withdrawn_at": result["withdrawn_at"]}


def test_repeated_withdrawal_is_idempotent_and_keeps_one_event():
    clock = Clock()
    svc, jobs, lifecycle, _ = make_system(clock)
    build_log(svc, clock, LOG)
    first = lifecycle.withdraw(STUDENT, LOG, reason="first")
    events_after_first = [e["type"] for e in svc.events(LOG)]

    second = lifecycle.withdraw(STUDENT, LOG, reason="second")

    assert second["replayed"] is True
    assert second["withdrawn_at"] == first["withdrawn_at"]
    assert second["event"]["hash"] == first["event"]["hash"]
    assert lifecycle._tombstone(LOG)["reason"] == "first"
    assert [e["type"] for e in svc.events(LOG)] == events_after_first
    assert [e["type"] for e in svc.events(LOG)].count("record.withdrawn") == 1


def test_a_running_compile_cannot_publish_after_withdrawal():
    clock = Clock()
    svc, jobs, lifecycle, _ = make_system(clock)
    build_log(svc, clock, LOG)
    claimed = jobs.queue.claim(worker_id="worker-a")
    assert claimed.kind == KIND_COMPILE

    lifecycle.withdraw(STUDENT, LOG)
    assert jobs.queue.get(claimed.id).state == "cancelled"

    with pytest.raises(RecordWithdrawn):
        jobs.handle_compile(claimed)
    assert lifecycle.receipts.get(LOG) is None
    assert lifecycle.receipts.artifacts(LOG) == {}
    with pytest.raises(LeaseLost):
        jobs.queue.complete(claimed, {"late": True})


def test_partial_question_outputs_cannot_be_stored_after_withdrawal():
    clock = Clock()
    calls = {"n": 0}

    def one_then_down(messages):
        calls["n"] += 1
        if calls["n"] == 2:
            raise LLMUnavailable("down")
        return llm_ask(messages)

    svc, jobs, lifecycle, _ = make_system(clock, ask=one_then_down)
    build_log(svc, clock, LOG)
    jobs.run_until_idle(max_jobs=1)  # v1; questions job queued
    questions_id = jobs.queue.db.execute(
        "SELECT id FROM jobs WHERE kind = ?", (KIND_QUESTIONS,)).fetchone()[0]
    questions_job = jobs.queue.get(questions_id)

    lifecycle.withdraw(STUDENT, LOG)
    assert lifecycle.receipts.artifacts(LOG) == {}

    with pytest.raises(RecordWithdrawn):
        jobs.handle_questions(questions_job)
    assert lifecycle.receipts.artifacts(LOG) == {}


def test_a_running_release_cannot_publish_after_withdrawal():
    clock = Clock()
    svc, jobs, lifecycle, _ = make_system(clock)
    build_log(svc, clock, LOG)
    jobs.run_until_idle(max_jobs=1)  # v1 and a queued questions job

    clock.t = parse(record(lifecycle)["base_at"])
    claimed = jobs.queue.claim(worker_id="worker-release")
    assert claimed.kind == "receipt.release"

    lifecycle.withdraw(STUDENT, LOG)
    assert lifecycle.handle_release(claimed) == {"status": "withdrawn"}
    assert record(lifecycle)["released_at"] is None
    with pytest.raises(LeaseLost):
        jobs.queue.complete(claimed, {"late": True})


def test_withdrawal_rolls_back_atomically_when_cancellation_fails(monkeypatch):
    clock = Clock()
    svc, jobs, lifecycle, _ = make_system(clock)
    build_log(svc, clock, LOG)
    jobs.run_until_idle(max_jobs=1)
    seal = submit_event(svc)["hash"]
    before = lifecycle.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V1)
    queued = job_states(jobs)

    def boom(*args, **kwargs):
        raise RuntimeError("cancellation failed")

    monkeypatch.setattr(lifecycle.queue, "cancel_by_log", boom)
    with pytest.raises(RuntimeError):
        lifecycle.withdraw(STUDENT, LOG)

    assert not [e for e in svc.events(LOG) if e["type"] == "record.withdrawn"]
    assert lifecycle._tombstone(LOG) is None
    after = lifecycle.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V1)
    assert after is not None and after.body == before.body
    assert job_states(jobs) == queued
    assert all(r[0] is None for r in svc.db.execute(
        "SELECT withdrawn_at FROM release_records WHERE log_id = ?", (LOG,)))


def test_after_release_withdrawal_is_refused_without_changes():
    clock = Clock()
    svc, jobs, lifecycle, _ = make_system(clock)
    build_log(svc, clock, LOG)
    jobs.run_until_idle()
    clock.t = parse(record(lifecycle)["base_at"])
    lifecycle.handle_release(release_job(jobs, lifecycle, PHASE_BASE))
    seal = submit_event(svc)["hash"]
    events_before = [e["type"] for e in svc.events(LOG)]

    with pytest.raises(AfterRelease):
        lifecycle.withdraw(STUDENT, LOG)

    assert lifecycle.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V2) is not None
    assert lifecycle._tombstone(LOG) is None
    assert [e["type"] for e in svc.events(LOG)] == events_before
    assert {r[0] for r in svc.db.execute("SELECT state FROM jobs")} != {"cancelled"}


# ---------------------------------------------------------------- scoping
def test_cross_log_and_cross_tenant_access_is_rejected():
    clock = Clock()
    scopes = {LOG: RecordScope(TENANT, OWNER), LOG2: RecordScope("tenant-2", "student-9")}
    svc, jobs, lifecycle, _ = make_system(clock, scopes=scopes)
    build_log(svc, clock, LOG)
    build_log(svc, clock, LOG2)
    jobs.run_until_idle()

    with pytest.raises(AccessDenied):
        lifecycle.withdraw(TENANT2_STUDENT, LOG)
    with pytest.raises(AccessDenied):
        lifecycle.withdraw(STUDENT_OTHER, LOG)
    with pytest.raises(AccessDenied):
        lifecycle.withdraw(Identity(TENANT, "teacher", OWNER), LOG)
    with pytest.raises(AccessDenied):
        lifecycle.teacher_view(TENANT2_TEACHER, LOG)
    with pytest.raises(AccessDenied):
        lifecycle.teacher_view(STUDENT, LOG)  # a student does not get the teacher view
    with pytest.raises(AccessDenied):
        lifecycle.teacher_view(TENANT2_TEACHER, "no-such-log")

    lifecycle.withdraw(STUDENT, LOG)
    assert lifecycle._tombstone(LOG) is not None
    assert lifecycle._tombstone(LOG2) is None
    seal2 = submit_event(svc, LOG2)["hash"]
    assert lifecycle.receipts.get(LOG2, seal_hash=seal2, version=RECEIPT_V1) is not None
    assert lifecycle.teacher_view(TENANT2_TEACHER, LOG2)["status"] == "compiling"


# ---------------------------------------------------------------- routes
def make_app(clock, *, identity_for=None, deadlines=None, scopes=None):
    providers = Providers(deadlines, scopes)
    return create_app(":memory:", clock, sources_for=lambda log_id: make_sources(),
                      deadline_for=providers.deadline_for, scope_for=providers.scope_for,
                      identity_for=identity_for, start_job_loop=False,
                      enable_lifecycle=True)


def test_generic_events_route_cannot_bypass_cancellation_and_deletion():
    clock = Clock()
    app = make_app(clock, identity_for=lambda log_id: STUDENT)
    with TestClient(app) as client:
        svc, jobs = app.state.events, app.state.jobs
        lifecycle = app.state.lifecycle
        build_log(svc, clock, LOG)
        jobs.run_until_idle(max_jobs=1)
        seal = submit_event(svc)["hash"]

        response = client.post(f"/logs/{LOG}/events",
                               json={"type": "record.withdrawn",
                                     "payload": {"reason": "changed my mind"}})
        assert response.status_code == 200, response.text
        assert response.json()["event"]["type"] == "record.withdrawn"
        assert [e["type"] for e in svc.events(LOG)].count("record.withdrawn") == 1
        assert lifecycle.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V1) is None
        assert lifecycle._tombstone(LOG) is not None
        assert not ({r[0] for r in jobs.queue.db.execute(
            "SELECT state FROM jobs")} & {"queued", "running"})
        assert svc.verify(LOG)["ok"] is True


def test_generic_events_route_fails_closed_without_lifecycle():
    clock = Clock()
    app = create_app(":memory:", clock, sources_for=lambda log_id: make_sources(),
                     start_job_loop=False, enable_lifecycle=False)
    with TestClient(app) as client:
        svc = app.state.events
        build_log(svc, clock, LOG)

        response = client.post(f"/logs/{LOG}/events",
                               json={"type": "record.withdrawn", "payload": {}})
        assert response.status_code == 403, response.text
        assert response.json() == {"error": "access_denied"}
        assert not [e for e in svc.events(LOG) if e["type"] == "record.withdrawn"]


def test_dedicated_withdrawal_route_and_fail_closed_identity():
    clock = Clock()
    app = make_app(clock, identity_for=lambda log_id: STUDENT)
    with TestClient(app) as client:
        svc, jobs = app.state.events, app.state.jobs
        build_log(svc, clock, LOG)
        response = client.post(f"/logs/{LOG}/withdraw", json={"reason": "my choice"})
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "record_removed"
        assert response.json()["replayed"] is False
        assert app.state.lifecycle._tombstone(LOG) is not None

    no_identity = make_app(Clock(), identity_for=None)
    with TestClient(no_identity) as client:
        response = client.post(f"/logs/{LOG}/withdraw", json={})
        assert response.status_code == 403
        assert response.json() == {"error": "access_denied"}


def test_withdrawal_route_after_release_returns_after_release():
    clock = Clock()
    app = make_app(clock, identity_for=lambda log_id: STUDENT)
    with TestClient(app) as client:
        svc, jobs = app.state.events, app.state.jobs
        lifecycle = app.state.lifecycle
        build_log(svc, clock, LOG)
        jobs.run_until_idle()
        clock.t = parse(record(lifecycle)["base_at"])
        JobRunner(jobs.queue, {**jobs.handlers(), **lifecycle.handlers()},
                  worker_id="release").run_until_idle()
        seal = submit_event(svc)["hash"]

        response = client.post(f"/logs/{LOG}/withdraw", json={})
        assert response.status_code == 409, response.text
        assert response.json() == {"error": "after_release"}
        assert lifecycle.receipts.get(LOG, seal_hash=seal, version=RECEIPT_V2) is not None
        assert lifecycle._tombstone(LOG) is None


def test_release_loop_runs_release_jobs_through_the_app_runner():
    clock = Clock()
    app = make_app(clock)
    svc, jobs, lifecycle = app.state.events, app.state.jobs, app.state.lifecycle
    build_log(svc, clock, LOG)
    jobs.run_until_idle()  # compile + questions; questions-ready job queued for base
    clock.t = parse(record(lifecycle)["base_at"])
    JobRunner(jobs.queue, {**jobs.handlers(), **lifecycle.handlers()},
              worker_id="release").run_until_idle()
    assert record(lifecycle)["released_at"] is not None
    assert record(lifecycle)["released_version"] == RECEIPT_V2
