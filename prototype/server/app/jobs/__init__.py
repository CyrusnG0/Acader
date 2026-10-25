"""Bounded durable job queue for the prototype server.

T-020 integration surface: construct :class:`JobQueue` on the app's autocommit SQLite
connection (or :meth:`JobQueue.open` for its own file). When sharing ``EventService.db``,
pass ``lock=event_service._lock`` so both services serialise every transaction through the
same lock. ``enqueue`` work with a stable idempotency key, then run :class:`JobRunner` with
one handler per job ``kind``. At submit, T-020 can join an existing transaction by passing
``conn=`` to ``enqueue`` while holding that lock. T-021 uses
``JobQueue.cancel_by_log(..., conn=)`` inside the ``record.withdrawn`` transaction.

See :mod:`app.jobs.queue` for leases, fairness, provider caps, retry timing and recovery.
"""
from .queue import (PRIORITY_MAPPER, PRIORITY_NORMAL, RETRY_DELAYS_MINUTES, STATES, Job,
                    JobQueue, JobQueueError, IdempotencyConflict, LeaseLost)
from .runner import Handler, JobRunner, PermanentJobError, RetryableJobError

__all__ = ["Job", "JobQueue", "JobQueueError", "IdempotencyConflict", "LeaseLost",
           "JobRunner", "Handler", "RetryableJobError", "PermanentJobError",
           "PRIORITY_NORMAL", "PRIORITY_MAPPER", "RETRY_DELAYS_MINUTES", "STATES"]
