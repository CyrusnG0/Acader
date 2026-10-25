"""Durable, bounded job queue (architecture.md §4, eng review D23; eng v2 D4/D6/D10).

One row per job in the same SQLite database as the event log. A job is claimed under
``BEGIN IMMEDIATE`` with a lease token, executed without any write transaction open, then
completed (or failed) under a second transaction. The token is the fence: a worker whose
lease was recovered, renewed by someone else, or cancelled cannot publish a result.

Design points T-020 and T-021 rely on:

- **Idempotent enqueue.** ``idempotency_key`` is unique. Repeating the same enqueue returns
  the stored job (also after a restart). Reusing a key with different job fields raises
  :class:`IdempotencyConflict`.
- **Bounded LLM work.** ``backend`` names the provider a job will call. At most
  ``max_per_backend`` (default 4) jobs with that backend may be running at once. Jobs with
  ``backend=None`` (parsing, replay, receipt assembly) do not take a provider slot. One
  running job is treated as one provider slot for its whole handler, which is a conservative
  bound on concurrent calls.
- **Fairness.** Same-priority jobs are served round-robin by submission, earliest submission
  first. A submission is ``submission_id``, defaulting to ``log_id`` when omitted; jobs with
  neither share one system bucket. Lowest priority is reserved for mapper jobs
  (:data:`PRIORITY_MAPPER`); the mapper itself is not implemented here.
- **Retries.** A retryable failure returns the job to ``queued`` with the D23 schedule
  1, 4, 16 minutes, then the last delay again. A non-retryable failure is terminal
  (``failed``). The queue invents no attempt limit; T-021 owns the release cap.
- **Cancellation.** ``cancel_by_log`` is a one-statement update that can join a caller-owned
  transaction. It fences running jobs too, so a result produced after cancellation is
  rejected. T-021 uses this for ``record.withdrawn``.
- **Restart recovery.** ``recover_expired`` (also called at the start of every claim) returns
  expired ``running`` jobs to ``queued``.

Connection rules: the SQLite connection must be in autocommit mode
(``isolation_level=None``, as ``EventStore`` creates it). A ``conn=`` argument means the
caller already holds both the write transaction and the serialisation for that connection;
the queue then neither begins, commits nor rolls back. Without ``conn`` the queue starts and
finishes its own transaction. Never share one connection across threads without such a
caller-held lock.
"""
from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable, Iterable

from engine.events import ts_seconds

STATES = ("queued", "running", "done", "failed", "cancelled")
PRIORITY_NORMAL = 0
PRIORITY_MAPPER = 100  # reserved: lowest priority for future mapper jobs (eng v2 D6)
RETRY_DELAYS_MINUTES = (1, 4, 16)

_DDL = """
CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT NOT NULL,
  idempotency_key TEXT NOT NULL UNIQUE,
  log_id TEXT,
  submission_id TEXT,
  priority INTEGER NOT NULL,
  backend TEXT,
  payload TEXT NOT NULL,
  state TEXT NOT NULL,
  attempts INTEGER NOT NULL DEFAULT 0,
  run_after TEXT NOT NULL,
  lease_token TEXT,
  lease_until TEXT,
  worker_id TEXT,
  result TEXT,
  error_kind TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  finished_at TEXT
);
CREATE INDEX IF NOT EXISTS jobs_state_run_after ON jobs (state, run_after);
CREATE INDEX IF NOT EXISTS jobs_log_state ON jobs (log_id, state);
CREATE INDEX IF NOT EXISTS jobs_backend_state ON jobs (backend, state);
CREATE TABLE IF NOT EXISTS job_submissions (
  submission_id TEXT PRIMARY KEY,
  first_seen INTEGER NOT NULL,
  turns INTEGER NOT NULL DEFAULT 0
);
"""

_COLUMN_NAMES = ("id", "kind", "idempotency_key", "log_id", "submission_id", "priority",
                 "backend", "payload", "state", "attempts", "run_after", "lease_token",
                 "lease_until", "worker_id", "result", "error_kind", "created_at",
                 "updated_at", "finished_at")
_COLUMNS = ", ".join(_COLUMN_NAMES)
_JOB_COLUMNS = ", ".join(f"j.{name}" for name in _COLUMN_NAMES)

_CLAIM_SQL = f"""
SELECT {_JOB_COLUMNS}
FROM jobs j
LEFT JOIN job_submissions s ON s.submission_id = COALESCE(j.submission_id, '')
LEFT JOIN (
  SELECT backend, COUNT(*) AS n
  FROM jobs
  WHERE state = 'running' AND backend IS NOT NULL
  GROUP BY backend
) r ON r.backend = j.backend
WHERE j.state = 'queued'
  AND j.run_after <= ?
  AND (j.backend IS NULL OR COALESCE(r.n, 0) < ?)
ORDER BY j.priority ASC,
         COALESCE(s.turns, 0) ASC,
         COALESCE(s.first_seen, 0) ASC,
         j.id ASC
LIMIT 1
"""


class JobQueueError(Exception):
    """Base class for queue errors."""


class IdempotencyConflict(JobQueueError):
    """The key exists but the new job describes different work."""

    def __init__(self, key: str):
        super().__init__(f"idempotency key {key!r} is already used by a different job")
        self.key = key


class LeaseLost(JobQueueError):
    """The caller no longer owns the job: it was recovered, completed, or cancelled."""


@dataclass(frozen=True)
class Job:
    id: int
    kind: str
    idempotency_key: str
    log_id: str | None
    submission_id: str | None
    priority: int
    backend: str | None
    payload: dict
    state: str
    attempts: int
    run_after: str
    lease_token: str | None
    lease_until: str | None
    worker_id: str | None
    result: dict | None
    error_kind: str | None
    created_at: str
    updated_at: str
    finished_at: str | None


def _default_clock() -> datetime:
    return datetime.now(timezone.utc)


def _job(row) -> Job:
    return Job(
        id=row[0], kind=row[1], idempotency_key=row[2], log_id=row[3],
        submission_id=row[4], priority=row[5], backend=row[6],
        payload=json.loads(row[7]), state=row[8], attempts=row[9], run_after=row[10],
        lease_token=row[11], lease_until=row[12], worker_id=row[13],
        result=json.loads(row[14]) if row[14] is not None else None,
        error_kind=row[15], created_at=row[16], updated_at=row[17], finished_at=row[18])


def _payload_json(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class JobQueue:
    """Durable queue storage. Construct with an existing autocommit SQLite connection."""

    def __init__(self, db: sqlite3.Connection, *, clock: Callable[[], datetime] | None = None,
                 lease_seconds: int = 300, max_per_backend: int = 4,
                 retry_delays_minutes: tuple[int, ...] = RETRY_DELAYS_MINUTES):
        if not isinstance(lease_seconds, int) or isinstance(lease_seconds, bool) \
                or lease_seconds <= 0:
            raise ValueError("lease_seconds must be a positive integer")
        if not isinstance(max_per_backend, int) or isinstance(max_per_backend, bool) \
                or max_per_backend <= 0:
            raise ValueError("max_per_backend must be a positive integer")
        delays = tuple(retry_delays_minutes)
        if not delays or not all(isinstance(d, int) and not isinstance(d, bool) and d >= 0
                                 for d in delays):
            raise ValueError("retry_delays_minutes must be a non-empty tuple of integers")
        self.db = db
        self.clock = clock or _default_clock
        self.lease_seconds = lease_seconds
        self.max_per_backend = max_per_backend
        self.retry_delays_minutes = delays
        self._lock = threading.RLock()
        self.db.executescript(_DDL)

    @classmethod
    def open(cls, path: str, **kwargs) -> "JobQueue":
        """Own a new connection to ``path`` (WAL for files). Caller must ``close()`` it."""
        db = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
        db.execute("PRAGMA busy_timeout=5000")
        if path != ":memory:":
            db.execute("PRAGMA journal_mode=WAL")
        return cls(db, **kwargs)

    def close(self) -> None:
        self.db.close()

    # ---- transactions and time ------------------------------------------------------------

    def _now(self) -> datetime:
        now = self.clock()
        if not isinstance(now, datetime) or now.tzinfo is None:
            raise ValueError("clock must return a timezone-aware datetime")
        return now

    @contextmanager
    def _write(self, conn: sqlite3.Connection | None):
        if conn is not None:
            yield conn  # the caller owns the transaction and its serialisation
            return
        with self._lock:
            self.db.execute("BEGIN IMMEDIATE")
            try:
                yield self.db
                self.db.execute("COMMIT")
            except BaseException:
                self.db.execute("ROLLBACK")
                raise

    def _row(self, db: sqlite3.Connection, job_id: int) -> Job:
        row = db.execute(f"SELECT {_COLUMNS} FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if row is None:
            raise LeaseLost("job no longer exists")
        return _job(row)

    # ---- enqueue --------------------------------------------------------------------------

    def enqueue(self, kind: str, *, idempotency_key: str, log_id: str | None = None,
                submission_id: str | None = None, priority: int = PRIORITY_NORMAL,
                backend: str | None = None, payload: dict | None = None,
                run_after: datetime | None = None,
                conn: sqlite3.Connection | None = None) -> Job:
        """Add one job, or return the stored one for the same key.

        ``submission_id`` defaults to ``log_id`` so all jobs for one submission share a fair
        queue turn; jobs with neither share one system bucket. ``backend`` is the provider the
        handler will call, or ``None`` when the handler makes no provider call.
        """
        if not isinstance(kind, str) or not kind:
            raise ValueError("kind must be a non-empty string")
        if not isinstance(idempotency_key, str) or not idempotency_key:
            raise ValueError("idempotency_key must be a non-empty string")
        if not isinstance(priority, int) or isinstance(priority, bool) or priority < 0:
            raise ValueError("priority must be a non-negative integer")
        if backend is not None and (not isinstance(backend, str) or not backend):
            raise ValueError("backend must be a non-empty string or None")
        if payload is None:
            payload = {}
        if not isinstance(payload, dict):
            raise ValueError("payload must be a dict")
        if submission_id is None:
            submission_id = log_id
        if submission_id is not None and not isinstance(submission_id, str):
            raise ValueError("submission_id must be a string or None")

        now = self._now()
        now_ts = ts_seconds(now)
        if run_after is not None:
            if not isinstance(run_after, datetime) or run_after.tzinfo is None:
                raise ValueError("run_after must be a timezone-aware datetime")
            run_after_ts = ts_seconds(run_after)
        else:
            run_after_ts = now_ts
        body = _payload_json(payload)

        with self._write(conn) as db:
            cur = db.execute(
                "INSERT OR IGNORE INTO jobs (kind, idempotency_key, log_id, submission_id, "
                "priority, backend, payload, state, attempts, run_after, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, 'queued', 0, ?, ?, ?)",
                (kind, idempotency_key, log_id, submission_id, priority, backend, body,
                 run_after_ts, now_ts, now_ts))
            row = db.execute(
                f"SELECT {_COLUMNS} FROM jobs WHERE idempotency_key = ?",
                (idempotency_key,)).fetchone()
            job = _job(row)
            if cur.rowcount == 0:
                same = (job.kind == kind and job.log_id == log_id
                        and job.submission_id == submission_id and job.priority == priority
                        and job.backend == backend and _payload_json(job.payload) == body)
                if not same:
                    raise IdempotencyConflict(idempotency_key)
                return job
            # Jobs with no submission share one bucket, so system work also takes fair turns.
            db.execute(
                "INSERT OR IGNORE INTO job_submissions (submission_id, first_seen, turns) "
                "SELECT ?, COALESCE(MAX(first_seen), 0) + 1, 0 FROM job_submissions",
                (submission_id if submission_id is not None else "",))
            return job

    def get(self, job_id: int) -> Job | None:
        row = self.db.execute(
            f"SELECT {_COLUMNS} FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return _job(row) if row else None

    # ---- claim, lease, completion ---------------------------------------------------------

    def claim(self, *, worker_id: str, conn: sqlite3.Connection | None = None) -> Job | None:
        """Claim the next fair, runnable job, or return ``None``.

        Expired running jobs are returned to ``queued`` first. A provider backend at its
        concurrency cap is skipped, so a free slot on another backend can be used.
        """
        if not isinstance(worker_id, str) or not worker_id:
            raise ValueError("worker_id must be a non-empty string")
        now = self._now()
        now_ts = ts_seconds(now)
        with self._write(conn) as db:
            self._recover_expired_in_tx(db, now_ts)
            row = db.execute(_CLAIM_SQL, (now_ts, self.max_per_backend)).fetchone()
            if row is None:
                return None
            job = _job(row)
            token = uuid.uuid4().hex
            lease_until = ts_seconds(now + timedelta(seconds=self.lease_seconds))
            db.execute(
                "UPDATE jobs SET state = 'running', attempts = attempts + 1, lease_token = ?, "
                "lease_until = ?, worker_id = ?, updated_at = ? "
                "WHERE id = ? AND state = 'queued'",
                (token, lease_until, worker_id, now_ts, job.id))
            db.execute(
                "UPDATE job_submissions SET turns = turns + 1 WHERE submission_id = ?",
                (job.submission_id if job.submission_id is not None else "",))
            return self._row(db, job.id)

    def renew(self, job: Job, *, conn: sqlite3.Connection | None = None) -> Job:
        """Extend a running job's lease. A different or cancelled owner raises ``LeaseLost``."""
        now = self._now()
        now_ts = ts_seconds(now)
        lease_until = ts_seconds(now + timedelta(seconds=self.lease_seconds))
        with self._write(conn) as db:
            cur = db.execute(
                "UPDATE jobs SET lease_until = ?, updated_at = ? "
                "WHERE id = ? AND state = 'running' AND lease_token = ?",
                (lease_until, now_ts, job.id, job.lease_token))
            if cur.rowcount == 0:
                raise LeaseLost(f"job {job.id} is not held by this worker")
            return self._row(db, job.id)

    def complete(self, job: Job, result: dict | None = None, *,
                 conn: sqlite3.Connection | None = None) -> Job:
        """Publish a result. Only the current lease token may complete a running job."""
        if result is not None and not isinstance(result, dict):
            raise ValueError("result must be a dict or None")
        now = self._now()
        now_ts = ts_seconds(now)
        stored = None if result is None else _payload_json(result)
        with self._write(conn) as db:
            cur = db.execute(
                "UPDATE jobs SET state = 'done', result = ?, lease_token = NULL, "
                "lease_until = NULL, worker_id = NULL, updated_at = ?, finished_at = ? "
                "WHERE id = ? AND state = 'running' AND lease_token = ?",
                (stored, now_ts, now_ts, job.id, job.lease_token))
            if cur.rowcount == 0:
                raise LeaseLost(f"job {job.id} is not held by this worker")
            return self._row(db, job.id)

    def fail(self, job: Job, *, error_kind: str, retryable: bool,
             conn: sqlite3.Connection | None = None) -> Job:
        """Record a failure. Retryable jobs wait on the D23 schedule; others are terminal.

        ``error_kind`` must be a short internal label (for example an LLM error class). Never
        pass prompt text, student text or provider messages.
        """
        if not isinstance(error_kind, str) or not error_kind:
            raise ValueError("error_kind must be a non-empty string")
        if not isinstance(retryable, bool):
            raise ValueError("retryable must be a bool")
        now = self._now()
        now_ts = ts_seconds(now)
        with self._write(conn) as db:
            row = db.execute(
                "SELECT attempts, state, lease_token FROM jobs WHERE id = ?",
                (job.id,)).fetchone()
            if row is None or row[1] != "running" or row[2] != job.lease_token:
                raise LeaseLost(f"job {job.id} is not held by this worker")
            attempts = row[0]
            if retryable:
                delay = self.retry_delays_minutes[
                    min(attempts - 1, len(self.retry_delays_minutes) - 1)]
                run_after = ts_seconds(now + timedelta(minutes=delay))
                db.execute(
                    "UPDATE jobs SET state = 'queued', run_after = ?, "
                    "lease_token = NULL, lease_until = NULL, worker_id = NULL, "
                    "error_kind = ?, updated_at = ? WHERE id = ? AND lease_token = ?",
                    (run_after, error_kind, now_ts, job.id, job.lease_token))
            else:
                db.execute(
                    "UPDATE jobs SET state = 'failed', lease_token = NULL, lease_until = NULL, "
                    "worker_id = NULL, error_kind = ?, updated_at = ?, finished_at = ? "
                    "WHERE id = ? AND lease_token = ?",
                    (error_kind, now_ts, now_ts, job.id, job.lease_token))
            return self._row(db, job.id)

    # ---- cancellation ---------------------------------------------------------------------

    def cancel_by_log(self, log_id: str, *, kinds: Iterable[str] | None = None,
                      reason: str = "cancelled",
                      conn: sqlite3.Connection | None = None) -> int:
        """Cancel queued and running jobs for one log; return how many changed.

        Running jobs are fenced immediately, so a handler that finishes later cannot publish
        its result. Pass ``conn`` to join a caller-owned transaction (T-021 withdrawal).
        """
        if not isinstance(log_id, str) or not log_id:
            raise ValueError("log_id must be a non-empty string")
        if not isinstance(reason, str) or not reason:
            raise ValueError("reason must be a non-empty string")
        now_ts = ts_seconds(self._now())
        sql = ("UPDATE jobs SET state = 'cancelled', lease_token = NULL, lease_until = NULL, "
               "worker_id = NULL, error_kind = ?, updated_at = ?, finished_at = ? "
               "WHERE log_id = ? AND state IN ('queued', 'running')")
        params: list = [reason, now_ts, now_ts, log_id]
        if kinds is not None:
            kinds = tuple(kinds)
            if not kinds or not all(isinstance(k, str) and k for k in kinds):
                raise ValueError("kinds must be a non-empty iterable of strings")
            sql += f" AND kind IN ({','.join('?' * len(kinds))})"
            params.extend(kinds)
        with self._write(conn) as db:
            cur = db.execute(sql, params)
            return cur.rowcount

    def cancel(self, job: Job, *, reason: str = "cancelled",
               conn: sqlite3.Connection | None = None) -> Job:
        """Cancel one job held by this worker, fencing its lease."""
        if not isinstance(reason, str) or not reason:
            raise ValueError("reason must be a non-empty string")
        now_ts = ts_seconds(self._now())
        with self._write(conn) as db:
            cur = db.execute(
                "UPDATE jobs SET state = 'cancelled', lease_token = NULL, lease_until = NULL, "
                "worker_id = NULL, error_kind = ?, updated_at = ?, finished_at = ? "
                "WHERE id = ? AND state = 'running' AND lease_token = ?",
                (reason, now_ts, now_ts, job.id, job.lease_token))
            if cur.rowcount == 0:
                raise LeaseLost(f"job {job.id} is not held by this worker")
            return self._row(db, job.id)

    # ---- recovery and observability -------------------------------------------------------

    def _recover_expired_in_tx(self, db: sqlite3.Connection, now_ts: str) -> int:
        cur = db.execute(
            "UPDATE jobs SET state = 'queued', run_after = ?, lease_token = NULL, "
            "lease_until = NULL, worker_id = NULL, updated_at = ? "
            "WHERE state = 'running' AND lease_until IS NOT NULL AND lease_until <= ?",
            (now_ts, now_ts, now_ts))
        return cur.rowcount

    def recover_expired(self, conn: sqlite3.Connection | None = None) -> int:
        """Return every expired running job to ``queued``. Call once at boot and per claim."""
        now_ts = ts_seconds(self._now())
        with self._write(conn) as db:
            return self._recover_expired_in_tx(db, now_ts)

    def stats(self) -> dict:
        """Counts by state plus running jobs per provider backend (operator page input)."""
        counts = {state: 0 for state in STATES}
        for state, n in self.db.execute("SELECT state, COUNT(*) FROM jobs GROUP BY state"):
            counts[state] = n
        by_backend = {b: n for b, n in self.db.execute(
            "SELECT backend, COUNT(*) FROM jobs WHERE state = 'running' "
            "AND backend IS NOT NULL GROUP BY backend")}
        return {"counts": counts, "running_by_backend": by_backend}
