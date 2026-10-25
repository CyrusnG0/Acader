"""Execute claimed jobs with injected handlers (architecture.md §4).

The runner never holds a write transaction while a handler runs: claim commits, then the
handler is called, then completion commits in a new transaction. Handlers return a JSON
dict, or raise :class:`RetryableJobError` / :class:`PermanentJobError` with a short internal
label. An unexpected exception is recorded by class name and is terminal; its message is
never stored (it could contain student text or a provider message).

``run_pending`` claims a small batch first and executes it in threads. The queue's
per-backend cap is enforced at claim time, so provider work stays bounded even when several
handlers run at once.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Callable

from .queue import Job, JobQueue, LeaseLost


class RetryableJobError(Exception):
    """Transient failure: the queue applies the D23 1/4/16-minute schedule."""

    def __init__(self, error_kind: str):
        if not isinstance(error_kind, str) or not error_kind:
            raise ValueError("error_kind must be a non-empty string")
        super().__init__(error_kind)
        self.error_kind = error_kind


class PermanentJobError(Exception):
    """Terminal failure: the job is not retried."""

    def __init__(self, error_kind: str):
        if not isinstance(error_kind, str) or not error_kind:
            raise ValueError("error_kind must be a non-empty string")
        super().__init__(error_kind)
        self.error_kind = error_kind


Handler = Callable[[Job], dict | None]


class JobRunner:
    def __init__(self, queue: JobQueue, handlers: dict[str, Handler], *,
                 worker_id: str = "runner"):
        if not isinstance(worker_id, str) or not worker_id:
            raise ValueError("worker_id must be a non-empty string")
        self.queue = queue
        self.handlers = dict(handlers)
        self.worker_id = worker_id

    def _finish(self, job: Job) -> None:
        """Apply the handler's outcome. A fenced job is already terminal elsewhere."""
        handler = self.handlers.get(job.kind)
        if handler is None:
            self._fail(job, "no_handler", retryable=False)
            return
        try:
            result = handler(job)
        except RetryableJobError as e:
            self._fail(job, e.error_kind, retryable=True)
        except PermanentJobError as e:
            self._fail(job, e.error_kind, retryable=False)
        except Exception as e:  # no message stored, only the class name
            self._fail(job, type(e).__name__, retryable=False)
        else:
            if result is not None and not isinstance(result, dict):
                self._fail(job, "bad_handler_result", retryable=False)
                return
            try:
                self.queue.complete(job, result)
            except LeaseLost:
                pass  # cancelled or recovered while the handler ran; no result is published

    def _fail(self, job: Job, error_kind: str, *, retryable: bool) -> None:
        try:
            self.queue.fail(job, error_kind=error_kind, retryable=retryable)
        except LeaseLost:
            pass

    def run_once(self) -> Job | None:
        """Claim and execute one job. Returns it, including when it was fenced."""
        job = self.queue.claim(worker_id=self.worker_id)
        if job is None:
            return None
        self._finish(job)
        return job

    def run_pending(self, *, max_concurrent: int = 8) -> int:
        """Claim up to ``max_concurrent`` jobs, execute them in threads, return how many."""
        if not isinstance(max_concurrent, int) or isinstance(max_concurrent, bool) \
                or max_concurrent <= 0:
            raise ValueError("max_concurrent must be a positive integer")
        jobs: list[Job] = []
        for _ in range(max_concurrent):
            job = self.queue.claim(worker_id=self.worker_id)
            if job is None:
                break
            jobs.append(job)
        if not jobs:
            return 0
        with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
            list(pool.map(self._finish, jobs))
        return len(jobs)

    def run_until_idle(self, *, max_jobs: int | None = None) -> int:
        """Execute runnable jobs one at a time until the queue returns none (or ``max_jobs``)."""
        done = 0
        while max_jobs is None or done < max_jobs:
            if self.run_once() is None:
                break
            done += 1
        return done
