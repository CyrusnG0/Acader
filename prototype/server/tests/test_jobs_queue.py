"""Durable job queue: idempotency, leases, fencing, fairness, caps, retries, cancellation.

All times come from an injected clock; no test sleeps and no provider is called.
"""
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import pytest

from app.events_service import EventService
from app.jobs import (MAX_ATTEMPTS, PRIORITY_MAPPER, PRIORITY_NORMAL, IdempotencyConflict,
                      JobQueue, JobRunner, LeaseLost, PermanentJobError, RetryableJobError)
from engine.events import ts_seconds

T0 = datetime(2026, 11, 2, 14, 0, 0, tzinfo=timezone.utc)


class Clock:
    def __init__(self, t=T0):
        self.t = t

    def __call__(self):
        return self.t

    def advance(self, **kw):
        self.t += timedelta(**kw)


class CountingLock:
    """Plain lock that signals when a second caller attempts to acquire it."""

    def __init__(self):
        self._lock = threading.Lock()
        self._guard = threading.Lock()
        self._count = 0
        self.second_acquire = threading.Event()

    def acquire(self, blocking=True, timeout=-1):
        with self._guard:
            self._count += 1
            if self._count >= 2:
                self.second_acquire.set()
        if timeout == -1:
            return self._lock.acquire(blocking)
        return self._lock.acquire(blocking, timeout)

    def release(self):
        self._lock.release()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *exc):
        self.release()
        return False


def connect():
    return sqlite3.connect(":memory:", isolation_level=None, check_same_thread=False)


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def db():
    conn = connect()
    yield conn
    conn.close()


@pytest.fixture
def queue(db, clock):
    return JobQueue(db, clock=clock)


def keys(jobs):
    return [j.idempotency_key for j in jobs]


# ---- idempotent enqueue ------------------------------------------------------------------------

def test_enqueue_defaults_and_submission_defaults_to_log(queue):
    job = queue.enqueue("compile", idempotency_key="k1", log_id="log-1")
    assert job.state == "queued"
    assert job.attempts == 0
    assert job.priority == PRIORITY_NORMAL
    assert job.backend is None
    assert job.log_id == "log-1"
    assert job.submission_id == "log-1"
    assert job.payload == {}
    assert job.run_after == ts_seconds(T0)
    assert job.lease_token is None


def test_repeated_enqueue_returns_the_same_job(queue):
    first = queue.enqueue("compile", idempotency_key="k1", log_id="log-1",
                          payload={"doc_rev": 3})
    again = queue.enqueue("compile", idempotency_key="k1", log_id="log-1",
                          payload={"doc_rev": 3})
    assert again.id == first.id
    assert queue.stats()["counts"]["queued"] == 1


@pytest.mark.parametrize("change", [
    {"kind": "l3"},
    {"log_id": "other"},
    {"payload": {"doc_rev": 4}},
    {"priority": PRIORITY_MAPPER},
    {"backend": "deepseek"},
])
def test_same_key_with_different_work_is_refused(queue, change):
    base = dict(kind="compile", idempotency_key="k1", log_id="log-1", payload={"doc_rev": 3})
    queue.enqueue(**base)
    with pytest.raises(IdempotencyConflict):
        queue.enqueue(**{**base, **change})


def test_enqueue_is_idempotent_across_a_restart(tmp_path, clock):
    path = str(tmp_path / "queue.db")
    first_queue = JobQueue.open(path, clock=clock)
    first = first_queue.enqueue("compile", idempotency_key="k1", log_id="log-1",
                                payload={"doc_rev": 3})
    first_queue.close()

    second_queue = JobQueue.open(path, clock=clock)
    try:
        again = second_queue.enqueue("compile", idempotency_key="k1", log_id="log-1",
                                     payload={"doc_rev": 3})
        assert again.id == first.id
        assert second_queue.stats()["counts"]["queued"] == 1
        with pytest.raises(IdempotencyConflict):
            second_queue.enqueue("compile", idempotency_key="k1", log_id="log-1",
                                 payload={"doc_rev": 4})
    finally:
        second_queue.close()


def test_concurrent_same_key_enqueue_creates_one_job(tmp_path, clock):
    path = str(tmp_path / "queue.db")
    setup = JobQueue.open(path, clock=clock)
    setup.close()
    start = threading.Barrier(4)

    def add(worker_id):
        own = JobQueue.open(path, clock=clock)
        try:
            start.wait()
            return own.enqueue("compile", idempotency_key="same", log_id="L1").id
        finally:
            own.close()

    with ThreadPoolExecutor(max_workers=4) as pool:
        ids = list(pool.map(add, range(4)))
    assert len(set(ids)) == 1

    check = JobQueue.open(path, clock=clock)
    try:
        assert check.stats()["counts"]["queued"] == 1
    finally:
        check.close()


def test_enqueue_can_join_a_caller_transaction(queue, db):
    db.execute("BEGIN IMMEDIATE")
    job = queue.enqueue("compile", idempotency_key="k1", log_id="log-1", conn=db)
    assert queue.get(job.id) is not None
    db.execute("ROLLBACK")
    assert queue.get(job.id) is None
    assert queue.stats()["counts"]["queued"] == 0


def test_injected_lock_serialises_two_components_on_one_connection(db, clock):
    lock = CountingLock()
    queue = JobQueue(db, clock=clock, lock=lock)
    assert queue._lock is lock

    # Component A (for example EventService) holds the shared lock and a transaction.
    lock.acquire()
    db.execute("BEGIN IMMEDIATE")
    db.execute("CREATE TABLE probe (value INTEGER)")
    result = {}

    def component_b():
        try:
            result["job"] = queue.enqueue("compile", idempotency_key="k1", log_id="L1")
        except BaseException as e:  # recorded so the main thread can assert
            result["error"] = e

    thread = threading.Thread(target=component_b)
    thread.start()
    assert lock.second_acquire.wait(timeout=5)  # the queue is waiting on the shared lock
    db.execute("COMMIT")
    lock.release()
    thread.join(timeout=5)

    assert not thread.is_alive()
    assert "error" not in result
    assert queue.get(result["job"].id) is not None


def test_caller_owned_transaction_does_not_reacquire_a_plain_lock(db, clock):
    lock = threading.Lock()
    queue = JobQueue(db, clock=clock, lock=lock)
    with lock:
        db.execute("BEGIN IMMEDIATE")
        job = queue.enqueue("compile", idempotency_key="k1", log_id="L1", conn=db)
        db.execute("COMMIT")
    assert queue.get(job.id) is not None


def test_caller_transaction_with_the_real_event_service_lock_and_connection(clock):
    service = EventService(":memory:", clock)
    try:
        queue = JobQueue(service.db, clock=clock, lock=service._lock)
        with service._lock:
            service.db.execute("BEGIN IMMEDIATE")
            job = queue.enqueue("compile", idempotency_key="k1", log_id="L1",
                                conn=service.db)
            service.db.execute("COMMIT")
        assert queue.get(job.id) is not None
    finally:
        service.close()


# ---- claim and lease ---------------------------------------------------------------------------

def test_claim_sets_running_lease_and_attempt(queue):
    queued = queue.enqueue("compile", idempotency_key="k1", log_id="log-1")
    claimed = queue.claim(worker_id="worker-a")
    assert claimed.id == queued.id
    assert claimed.state == "running"
    assert claimed.attempts == 1
    assert claimed.worker_id == "worker-a"
    assert claimed.lease_token and claimed.lease_token != ""
    assert claimed.lease_until == ts_seconds(T0 + timedelta(seconds=300))
    assert queue.claim(worker_id="worker-b") is None


def test_concurrent_claims_never_duplicate_a_job(tmp_path, clock):
    path = str(tmp_path / "queue.db")
    setup = JobQueue.open(path, clock=clock)
    for i in range(12):
        setup.enqueue("compile", idempotency_key=f"k{i}", log_id=f"log-{i}")
    setup.close()

    start = threading.Barrier(4)

    def drain(worker_id):
        own = JobQueue.open(path, clock=clock)
        try:
            start.wait()
            claimed = []
            while True:
                job = own.claim(worker_id=worker_id)
                if job is None:
                    return claimed
                claimed.append(job.id)
        finally:
            own.close()

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(drain, ["w1", "w2", "w3", "w4"]))
    claimed = [job_id for group in results for job_id in group]
    assert len(claimed) == 12
    assert len(set(claimed)) == 12


def test_expired_lease_is_recovered_and_can_be_claimed_again(queue, clock):
    queue.enqueue("compile", idempotency_key="k1", log_id="L1")
    first = queue.claim(worker_id="w1")
    clock.advance(seconds=301)
    assert queue.recover_expired() == 1
    recovered = queue.get(first.id)
    assert recovered.state == "queued"
    assert recovered.attempts == 1
    assert recovered.lease_token is None
    assert recovered.lease_until is None

    second = queue.claim(worker_id="w2")
    assert second.id == first.id
    assert second.attempts == 2
    assert second.lease_token != first.lease_token


def test_claim_itself_recovers_an_expired_lease(queue, clock):
    queue.enqueue("compile", idempotency_key="k1", log_id="L1")
    first = queue.claim(worker_id="w1")
    clock.advance(seconds=301)
    second = queue.claim(worker_id="w2")
    assert second.id == first.id
    assert second.attempts == 2


def test_restart_recovery_reclaims_running_jobs(tmp_path, clock):
    path = str(tmp_path / "queue.db")
    before = JobQueue.open(path, clock=clock)
    job = before.enqueue("compile", idempotency_key="k1", log_id="log-1")
    running = before.claim(worker_id="w1")
    before.close()

    clock.advance(seconds=301)
    after = JobQueue.open(path, clock=clock)
    try:
        assert after.recover_expired() == 1
        reclaimed = after.claim(worker_id="w2")
        assert reclaimed.id == job.id
        assert reclaimed.attempts == 2
        assert reclaimed.lease_token != running.lease_token
    finally:
        after.close()


def test_stale_completion_is_rejected_after_recovery(queue, clock):
    queue.enqueue("compile", idempotency_key="k1", log_id="L1")
    stale = queue.claim(worker_id="w1")
    clock.advance(seconds=301)
    fresh = queue.claim(worker_id="w2")
    assert fresh.lease_token != stale.lease_token

    with pytest.raises(LeaseLost):
        queue.complete(stale, {"published": True})
    current = queue.get(stale.id)
    assert current.state == "running"
    assert current.result is None

    done = queue.complete(fresh, {"published": "current"})
    assert done.state == "done"
    assert done.result == {"published": "current"}


def test_completion_is_once_and_clears_the_lease(queue):
    queue.enqueue("compile", idempotency_key="k1", log_id="L1")
    claimed = queue.claim(worker_id="w1")
    done = queue.complete(claimed, {"ok": True})
    assert done.state == "done"
    assert done.result == {"ok": True}
    assert done.lease_token is None
    assert done.lease_until is None
    assert done.finished_at is not None
    with pytest.raises(LeaseLost):
        queue.complete(claimed, {"ok": "again"})


def test_renew_extends_only_the_current_lease(queue, clock):
    queue.enqueue("compile", idempotency_key="k1", log_id="L1")
    claimed = queue.claim(worker_id="w1")
    clock.advance(seconds=200)
    renewed = queue.renew(claimed)
    assert renewed.lease_until == ts_seconds(clock.t + timedelta(seconds=300))
    assert renewed.lease_token == claimed.lease_token

    clock.advance(seconds=400)
    queue.recover_expired()
    with pytest.raises(LeaseLost):
        queue.renew(claimed)


# ---- retry schedule ----------------------------------------------------------------------------

def test_retry_schedule_is_exactly_one_four_sixteen_then_sixteen(queue, clock):
    queue.enqueue("compile", idempotency_key="k1", log_id="log-1")
    for attempt, delay in enumerate((1, 4, 16, 16), start=1):
        job = queue.claim(worker_id="w1")
        assert job.attempts == attempt
        failed = queue.fail(job, error_kind="timeout", retryable=True)
        assert failed.state == "queued"
        assert failed.error_kind == "timeout"
        assert failed.run_after == ts_seconds(clock.t + timedelta(minutes=delay))
        assert queue.claim(worker_id="w1") is None  # not due yet
        clock.advance(minutes=delay)


def test_retry_stops_after_five_attempts(queue, clock):
    assert MAX_ATTEMPTS == 5
    queue.enqueue("compile", idempotency_key="k1", log_id="log-1")
    for attempt, delay in enumerate((1, 4, 16, 16), start=1):
        job = queue.claim(worker_id="w1")
        assert job.attempts == attempt
        failed = queue.fail(job, error_kind="timeout", retryable=True)
        assert failed.state == "queued"
        assert failed.run_after == ts_seconds(clock.t + timedelta(minutes=delay))
        clock.advance(minutes=delay)

    fifth = queue.claim(worker_id="w1")
    assert fifth.attempts == 5
    failed = queue.fail(fifth, error_kind="timeout", retryable=True)
    assert failed.state == "failed"
    assert failed.error_kind == "timeout"
    assert failed.finished_at == ts_seconds(clock.t)
    assert failed.lease_token is None
    clock.advance(days=30)
    assert queue.claim(worker_id="w1") is None


def test_custom_attempt_limit(db, clock):
    queue = JobQueue(db, clock=clock, max_attempts=2)
    queue.enqueue("compile", idempotency_key="k1", log_id="L1")
    first = queue.claim(worker_id="w1")
    assert queue.fail(first, error_kind="timeout", retryable=True).state == "queued"
    clock.advance(minutes=1)
    second = queue.claim(worker_id="w1")
    assert second.attempts == 2
    failed = queue.fail(second, error_kind="timeout", retryable=True)
    assert failed.state == "failed"
    assert failed.finished_at is not None


@pytest.mark.parametrize("value", [0, -1, True, "5", None, 1.5])
def test_invalid_attempt_limit_is_refused(db, clock, value):
    with pytest.raises(ValueError):
        JobQueue(db, clock=clock, max_attempts=value)


def _exhaust(queue, clock):
    """Drive one job through all five attempts; the fifth failure is terminal."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        job = queue.claim(worker_id="w1")
        assert job.attempts == attempt
        failed = queue.fail(job, error_kind="timeout", retryable=True)
        if attempt < MAX_ATTEMPTS:
            assert failed.state == "queued"
            clock.advance(minutes=16)
    return failed


def test_on_failed_called_once_for_an_exhausted_job(db, clock):
    seen = []
    queue = JobQueue(db, clock=clock, on_failed=lambda conn, job: seen.append(job))
    queue.enqueue("compile", idempotency_key="k1", log_id="L1")
    failed = _exhaust(queue, clock)
    assert len(seen) == 1
    assert seen[0].id == failed.id
    assert seen[0].state == "failed"
    assert seen[0].attempts == MAX_ATTEMPTS


def test_on_failed_called_once_for_a_non_retryable_failure(db, clock):
    seen = []
    queue = JobQueue(db, clock=clock, on_failed=lambda conn, job: seen.append(job))
    queue.enqueue("compile", idempotency_key="k1", log_id="L1")
    job = queue.claim(worker_id="w1")
    queue.fail(job, error_kind="auth", retryable=False)
    assert len(seen) == 1
    assert seen[0].state == "failed"
    assert seen[0].error_kind == "auth"


def test_on_failed_not_called_for_retry_complete_or_cancel(db, clock):
    seen = []
    queue = JobQueue(db, clock=clock, on_failed=lambda conn, job: seen.append(job))
    queue.enqueue("compile", idempotency_key="retry", log_id="L1")
    retried = queue.claim(worker_id="w1")
    queue.fail(retried, error_kind="timeout", retryable=True)
    assert seen == []

    queue.enqueue("compile", idempotency_key="done", log_id="L2")
    done = queue.claim(worker_id="w1")
    queue.complete(done, {"ok": True})
    assert seen == []

    queue.enqueue("compile", idempotency_key="cancel", log_id="L3")
    cancelled = queue.claim(worker_id="w1")
    queue.cancel(cancelled)
    queue.cancel_by_log("L1")
    assert seen == []


def test_on_failed_runs_inside_the_write_transaction(db, clock):
    seen = {}

    def hook(conn, job):
        seen["in_transaction"] = conn.in_transaction
        seen["job"] = job

    queue = JobQueue(db, clock=clock, on_failed=hook)
    queue.enqueue("compile", idempotency_key="k1", log_id="L1")
    job = queue.claim(worker_id="w1")
    queue.fail(job, error_kind="auth", retryable=False)
    assert seen["in_transaction"] is True
    assert seen["job"].state == "failed"


def test_on_failed_exception_rolls_back_the_failure(db, clock):
    def hook(conn, job):
        raise RuntimeError("operator alert not written")

    queue = JobQueue(db, clock=clock, on_failed=hook)
    queue.enqueue("compile", idempotency_key="k1", log_id="L1")
    job = queue.claim(worker_id="w1")
    with pytest.raises(RuntimeError):
        queue.fail(job, error_kind="auth", retryable=False)
    stored = queue.get(job.id)
    assert stored.state == "running"
    assert stored.lease_token == job.lease_token
    assert stored.finished_at is None


def test_expired_lease_at_the_attempt_limit_fails_the_job(db, clock):
    seen = []
    queue = JobQueue(db, clock=clock, on_failed=lambda conn, job: seen.append(job))
    queue.enqueue("compile", idempotency_key="k1", log_id="L1")
    for attempt in range(1, MAX_ATTEMPTS):
        claimed = queue.claim(worker_id="w1")
        assert claimed.attempts == attempt
        clock.advance(seconds=301)  # expire the lease; the next claim recovers it
    last = queue.claim(worker_id="w1")
    assert last.attempts == MAX_ATTEMPTS
    assert seen == []  # recoveries under the limit only requeue

    clock.advance(seconds=301)
    assert queue.recover_expired() == 1
    failed = queue.get(last.id)
    assert failed.state == "failed"
    assert failed.error_kind == "lease_expired"
    assert failed.finished_at is not None
    assert failed.lease_token is None
    assert len(seen) == 1 and seen[0].id == last.id
    assert queue.claim(worker_id="w1") is None


def test_expired_lease_under_the_limit_is_requeued_without_the_hook(db, clock):
    seen = []
    queue = JobQueue(db, clock=clock, on_failed=lambda conn, job: seen.append(job))
    queue.enqueue("compile", idempotency_key="k1", log_id="L1")
    queue.claim(worker_id="w1")
    clock.advance(seconds=301)
    assert queue.recover_expired() == 1
    assert queue.get(1).state == "queued"
    assert seen == []


def test_non_retryable_failure_is_terminal(queue, clock):
    queue.enqueue("compile", idempotency_key="k1", log_id="L1")
    job = queue.claim(worker_id="w1")
    failed = queue.fail(job, error_kind="auth", retryable=False)
    assert failed.state == "failed"
    assert failed.error_kind == "auth"
    assert failed.finished_at is not None
    clock.advance(hours=1)
    assert queue.claim(worker_id="w1") is None


def test_recovered_failure_keeps_the_attempt_count(queue, clock):
    queue.enqueue("compile", idempotency_key="k1", log_id="L1")
    job = queue.claim(worker_id="w1")
    queue.fail(job, error_kind="rate_limited", retryable=True)
    clock.advance(minutes=1)
    again = queue.claim(worker_id="w1")
    assert again.attempts == 2
    assert again.run_after == ts_seconds(clock.t)


# ---- fairness, priorities and provider caps ----------------------------------------------------

def test_round_robin_serves_one_job_per_submission_earliest_first(queue):
    for key, log in (("a1", "A"), ("a2", "A"), ("a3", "A"),
                     ("b1", "B"), ("b2", "B"), ("c1", "C")):
        queue.enqueue("compile", idempotency_key=key, log_id=log)

    claimed = [queue.claim(worker_id="w1") for _ in range(6)]
    assert keys(claimed) == ["a1", "b1", "c1", "a2", "b2", "a3"]


def test_jobs_without_a_submission_share_one_fair_bucket(queue):
    queue.enqueue("parse", idempotency_key="p1")
    queue.enqueue("parse", idempotency_key="p2")
    queue.enqueue("compile", idempotency_key="c1", log_id="L")

    claimed = [queue.claim(worker_id="w1") for _ in range(3)]
    assert keys(claimed) == ["p1", "c1", "p2"]


def test_lowest_priority_mapper_jobs_wait_for_normal_work(queue):
    mapper = queue.enqueue("map_suggest", idempotency_key="map", log_id="M",
                           priority=PRIORITY_MAPPER, backend="deepseek")
    normal = queue.enqueue("compile", idempotency_key="compile", log_id="N",
                           priority=PRIORITY_NORMAL)
    assert queue.claim(worker_id="w1").id == normal.id
    assert queue.claim(worker_id="w1").id == mapper.id


def test_four_running_calls_per_backend_and_independent_backends(queue):
    for i in range(6):
        queue.enqueue("compile", idempotency_key=f"d{i}", log_id=f"L{i}", backend="deepseek")
    queue.enqueue("compile", idempotency_key="o1", log_id="O", backend="openai_compat")
    queue.enqueue("replay", idempotency_key="n1", log_id="N")  # no provider call

    claimed = [queue.claim(worker_id="w1") for _ in range(6)]
    assert keys(claimed) == ["d0", "d1", "d2", "d3", "o1", "n1"]
    assert queue.claim(worker_id="w1") is None
    assert queue.stats()["running_by_backend"] == {"deepseek": 4, "openai_compat": 1}

    queue.complete(claimed[0], {"ok": True})
    next_job = queue.claim(worker_id="w1")
    assert next_job.idempotency_key == "d4"


def test_expired_lease_frees_its_provider_slot(queue, clock):
    for i in range(4):
        queue.enqueue("compile", idempotency_key=f"d{i}", log_id=f"L{i}", backend="deepseek")
    running = [queue.claim(worker_id="w1") for _ in range(4)]
    assert queue.claim(worker_id="w1") is None

    clock.advance(seconds=301)
    recovered = queue.claim(worker_id="w2")
    assert recovered.id in {job.id for job in running}
    assert recovered.attempts == 2


# ---- cancellation ------------------------------------------------------------------------------

def test_cancel_by_log_fences_queued_and_running_jobs(queue):
    done_job = queue.enqueue("compile", idempotency_key="done", log_id="L1")
    queue.complete(queue.claim(worker_id="w1"), {"ok": True})
    assert queue.get(done_job.id).state == "done"

    queue.enqueue("compile", idempotency_key="c1", log_id="L1")
    queue.enqueue("l3", idempotency_key="c2", log_id="L1")
    queue.enqueue("compile", idempotency_key="other", log_id="L2")
    other_log = queue.claim(worker_id="w2")  # L2 has fewer turns, so it is first
    assert other_log.idempotency_key == "other"
    running = queue.claim(worker_id="w3")
    assert running.log_id == "L1"

    assert queue.cancel_by_log("L1", reason="record.withdrawn") == 2
    assert queue.get(running.id).state == "cancelled"
    assert queue.get(done_job.id).state == "done"
    assert queue.get(other_log.id).state == "running"  # another log is untouched
    with pytest.raises(LeaseLost):
        queue.complete(running, {"published": True})
    assert queue.claim(worker_id="w4") is None
    assert queue.complete(other_log, {"ok": True}).state == "done"


def test_cancel_by_log_can_join_a_caller_transaction(queue, db):
    queue.enqueue("compile", idempotency_key="c1", log_id="L1")
    queue.enqueue("l3", idempotency_key="c2", log_id="L1")

    db.execute("BEGIN IMMEDIATE")
    assert queue.cancel_by_log("L1", reason="record.withdrawn", conn=db) == 2
    db.execute("ROLLBACK")

    assert queue.stats()["counts"]["queued"] == 2
    assert queue.stats()["counts"]["cancelled"] == 0


def test_cancel_by_log_can_select_kinds(queue):
    queue.enqueue("compile", idempotency_key="c1", log_id="L1")
    queue.enqueue("l3", idempotency_key="c2", log_id="L1")
    assert queue.cancel_by_log("L1", kinds=["l3"], reason="record.withdrawn") == 1
    job = queue.enqueue("compile", idempotency_key="c1", log_id="L1")
    assert job.state == "queued"
    other = queue.enqueue("l3", idempotency_key="c2", log_id="L1")
    assert other.state == "cancelled"


# ---- runner ------------------------------------------------------------------------------------

def test_runner_calls_the_handler_with_no_write_transaction_open(queue):
    seen = {}

    def handler(job):
        seen["in_transaction"] = queue.db.in_transaction
        seen["state"] = job.state
        return {"artifact": 7}

    queue.enqueue("compile", idempotency_key="k1", log_id="L1")
    runner = JobRunner(queue, {"compile": handler}, worker_id="runner-a")

    job = runner.run_once()
    assert job is not None
    assert seen == {"in_transaction": False, "state": "running"}
    finished = queue.get(job.id)
    assert finished.state == "done"
    assert finished.result == {"artifact": 7}
    assert finished.worker_id is None


def test_runner_retries_a_retryable_error(queue, clock):
    def handler(job):
        raise RetryableJobError("timeout")

    queue.enqueue("compile", idempotency_key="k1", log_id="L1")
    runner = JobRunner(queue, {"compile": handler})
    runner.run_once()

    job = queue.get(1)
    assert job.state == "queued"
    assert job.error_kind == "timeout"
    assert job.run_after == ts_seconds(clock.t + timedelta(minutes=1))
    assert job.attempts == 1


def test_runner_stops_after_five_retryable_failures(queue, clock):
    def handler(job):
        raise RetryableJobError("llm_unavailable")

    queue.enqueue("compile", idempotency_key="k1", log_id="L1")
    runner = JobRunner(queue, {"compile": handler})
    for _ in range(MAX_ATTEMPTS - 1):
        runner.run_once()
        assert queue.get(1).state == "queued"
        clock.advance(minutes=17)

    runner.run_once()
    job = queue.get(1)
    assert job.state == "failed"
    assert job.attempts == MAX_ATTEMPTS
    assert job.error_kind == "llm_unavailable"
    assert job.finished_at is not None
    assert runner.run_once() is None


def test_runner_stops_on_a_permanent_error(queue):
    def handler(job):
        raise PermanentJobError("schema")

    queue.enqueue("compile", idempotency_key="k1", log_id="L1")
    JobRunner(queue, {"compile": handler}).run_once()
    job = queue.get(1)
    assert job.state == "failed"
    assert job.error_kind == "schema"


def test_runner_stores_no_message_from_an_unexpected_exception(queue):
    def handler(job):
        raise RuntimeError("student wrote this sentence")

    queue.enqueue("compile", idempotency_key="k1", log_id="L1")
    JobRunner(queue, {"compile": handler}).run_once()
    job = queue.get(1)
    assert job.state == "failed"
    assert job.error_kind == "RuntimeError"
    assert job.result is None


def test_runner_fails_a_job_with_no_handler(queue):
    queue.enqueue("parse", idempotency_key="k1", log_id="L1")
    JobRunner(queue, {}).run_once()
    job = queue.get(1)
    assert job.state == "failed"
    assert job.error_kind == "no_handler"


def test_runner_publish_after_cancel_is_discarded(queue):
    def handler(job):
        queue.cancel_by_log("L1", reason="record.withdrawn")
        return {"lesson": "too late"}

    queue.enqueue("compile", idempotency_key="k1", log_id="L1")
    runner = JobRunner(queue, {"compile": handler})
    runner.run_once()
    job = queue.get(1)
    assert job.state == "cancelled"
    assert job.result is None


def test_runner_pending_respects_the_provider_cap(queue):
    def handler(job):
        return {"ok": job.id}

    for i in range(6):
        queue.enqueue("compile", idempotency_key=f"d{i}", log_id=f"L{i}", backend="deepseek")
    for i in range(2):
        queue.enqueue("replay", idempotency_key=f"n{i}", log_id=f"N{i}")

    runner = JobRunner(queue, {"compile": handler, "replay": handler})
    assert runner.run_pending(max_concurrent=8) == 6
    assert queue.stats()["counts"]["done"] == 6
    assert queue.stats()["running_by_backend"] == {}

    # The two remaining deepseek jobs wait for a free slot, not for the clock.
    assert runner.run_pending(max_concurrent=8) == 2
    assert queue.stats()["counts"]["done"] == 8


def test_stats_reports_each_state(queue):
    queue.enqueue("compile", idempotency_key="a", log_id="L1")
    queue.enqueue("compile", idempotency_key="b", log_id="L2")
    queue.claim(worker_id="w1")
    queue.cancel_by_log("L2")
    stats = queue.stats()
    assert stats["counts"] == {"queued": 0, "running": 1, "done": 0, "failed": 0,
                               "cancelled": 1}
