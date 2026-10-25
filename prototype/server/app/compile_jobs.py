"""Compile jobs for a seal: replay and receipt v1, then the L3e question upgrade to v2.

Every `submit` event schedules durable work in the same transaction as the seal:

- ``receipt.compile`` replays the log, records replay-mismatch operator alerts and issues
  receipt version 1 with no model call (every question is pending).
- ``receipt.questions`` runs the existing grounded question path and issues receipt version 2,
  reusing any outputs already stored (a retry never asks an answered question again).

A stored receipt is immutable and `receipt.issued` is written once per version, so re-running
a job is idempotent. Model calls always happen with no write transaction open.
"""
from __future__ import annotations

import json

from app.compile_service import (ensure_alerts_table, insert_alert_in_tx, record_alerts)
from app.events_service import EventService, LogNotFound
from app.jobs import (IdempotencyConflict, JobQueue, JobRunner, PermanentJobError,
                      PRIORITY_NORMAL, RetryableJobError)
from app.llm import default_backend
from app.receipt_service import (build_receipt, llm_ask, _persist, store_artifacts,
                                 stored_receipt)
from app.receipt_store import ReceiptStore
from engine.events import ts_seconds
from engine.provenance import operator_alerts
from engine.receipt import LLMUnavailable

KIND_COMPILE = "receipt.compile"
KIND_QUESTIONS = "receipt.questions"
RECEIPT_V1 = 1
RECEIPT_V2 = 2


def compile_key(log_id: str, seal_hash: str) -> str:
    return f"{KIND_COMPILE}:{log_id}:{seal_hash}"


def questions_key(log_id: str, seal_hash: str) -> str:
    return f"{KIND_QUESTIONS}:{log_id}:{seal_hash}"


def _payload(seal: dict) -> dict:
    return {"seal_hash": seal["hash"], "seal_seq": seal["seq"],
            "doc_rev": seal["payload"]["doc_rev"]}


def _identifiers(res) -> dict:
    receipt = res.receipt
    return {"receipt_id": receipt["receipt_id"], "receipt_hash": res.receipt_hash,
            "version": receipt["version"], "status": receipt["status"]}


class CompileJobs:
    """Durable submit-to-receipt jobs on the EventService connection and lock."""

    def __init__(self, service: EventService, *, sources_for, block_kinds_for=None,
                 ask=llm_ask, stamp=None, backend=None, receipts=None,
                 worker_id: str = "compile", **queue_kwargs):
        self.service = service
        self.sources_for = sources_for
        self.block_kinds_for = block_kinds_for
        self.ask = ask
        self.stamp = stamp
        self.backend = backend if backend is not None else default_backend()
        self.receipts = receipts or ReceiptStore(service.db)
        self.worker_id = worker_id
        ensure_alerts_table(service)
        self.queue = JobQueue(service.db, lock=service._lock, clock=service.clock,
                              on_failed=self._on_failed, **queue_kwargs)
        service.add_seal_hook(self.on_seal)

    # ---- scheduling -----------------------------------------------------------------------

    def on_seal(self, log_id: str, submit_event: dict, db) -> None:
        """Schedule the compile job inside the submit transaction (the lock is already held)."""
        self.queue.enqueue(KIND_COMPILE, idempotency_key=compile_key(log_id, submit_event["hash"]),
                           log_id=log_id, priority=PRIORITY_NORMAL, backend=None,
                           payload=_payload(submit_event), conn=db)

    def reconcile(self) -> int:
        """Recreate missing work after a crash or restart; return how many jobs were new.

        Idempotent by key, so a failed or finished job is never requeued here.
        """
        self.queue.recover_expired()
        with self.service._lock:
            submit_rows = self.service.db.execute(
                "SELECT body FROM events WHERE type = 'submit' ORDER BY log_id, seq").fetchall()
            receipt_rows = self.service.db.execute(
                "SELECT log_id, seal_hash, body FROM receipts WHERE version = ?",
                (RECEIPT_V1,)).fetchall()
            with_v2 = {(r[0], r[1]) for r in self.service.db.execute(
                "SELECT log_id, seal_hash FROM receipts WHERE version = ?", (RECEIPT_V2,))}
            existing = {r[0] for r in self.service.db.execute(
                "SELECT idempotency_key FROM jobs")}
        submits = [json.loads(r[0]) for r in submit_rows]
        by_seal = {(e["log_id"], e["hash"]): e for e in submits}
        created = 0
        for e in submits:
            key = compile_key(e["log_id"], e["hash"])
            self.queue.enqueue(KIND_COMPILE, idempotency_key=key, log_id=e["log_id"],
                               priority=PRIORITY_NORMAL, backend=None, payload=_payload(e))
            if key not in existing:
                existing.add(key)
                created += 1
        for log_id, seal_hash, body in receipt_rows:
            receipt = json.loads(bytes(body).decode("utf-8"))
            if not receipt.get("questions_pending") or (log_id, seal_hash) in with_v2:
                continue
            seal = by_seal.get((log_id, seal_hash))
            if seal is None:
                continue
            key = questions_key(log_id, seal_hash)
            self.queue.enqueue(KIND_QUESTIONS, idempotency_key=key, log_id=log_id,
                               priority=PRIORITY_NORMAL, backend=self.backend,
                               payload=_payload(seal))
            if key not in existing:
                existing.add(key)
                created += 1
        return created

    # ---- handlers -------------------------------------------------------------------------

    def _seal_event(self, log_id: str, seal_hash: str) -> dict | None:
        try:
            events = self.service.events(log_id)
        except LogNotFound:
            return None
        return next((e for e in events if e["type"] == "submit" and e["hash"] == seal_hash),
                    None)

    def _enqueue_questions(self, log_id: str, seal: dict) -> None:
        try:
            self.queue.enqueue(KIND_QUESTIONS,
                               idempotency_key=questions_key(log_id, seal["hash"]),
                               log_id=log_id, priority=PRIORITY_NORMAL, backend=self.backend,
                               payload=_payload(seal))
        except IdempotencyConflict:
            pass  # the existing job stands

    def handle_compile(self, job) -> dict:
        log_id = job.log_id
        seal_hash = (job.payload or {}).get("seal_hash")
        if not isinstance(log_id, str) or not isinstance(seal_hash, str):
            raise PermanentJobError("seal_missing")
        issued = stored_receipt(self.service, self.receipts, log_id, seal_hash=seal_hash,
                                version=RECEIPT_V1)
        seal = None
        if issued is not None:
            res, _ = issued
        else:
            seal = self._seal_event(log_id, seal_hash)
            if seal is None:
                raise PermanentJobError("seal_missing")
            block_kinds = self.block_kinds_for(log_id) if self.block_kinds_for else None
            res, compile_result = build_receipt(
                self.service, log_id, self.sources_for(log_id), seal_hash=seal_hash,
                version=RECEIPT_V1, ask=None, stored={}, stamp=self.stamp,
                block_kinds=block_kinds)
            record_alerts(self.service, log_id, operator_alerts(compile_result, log_id))
            res, _ = _persist(self.service, self.receipts, log_id, res, version=RECEIPT_V1)
        if res.receipt["questions_pending"]:
            if seal is None:
                seal = self._seal_event(log_id, seal_hash)
                if seal is None:
                    raise PermanentJobError("seal_missing")
            self._enqueue_questions(log_id, seal)
        return _identifiers(res)

    def handle_questions(self, job) -> dict:
        log_id = job.log_id
        payload = job.payload or {}
        seal_hash = payload.get("seal_hash")
        if not isinstance(log_id, str) or not isinstance(seal_hash, str):
            raise PermanentJobError("seal_missing")
        issued = stored_receipt(self.service, self.receipts, log_id, seal_hash=seal_hash,
                                version=RECEIPT_V2)
        if issued is not None:
            return _identifiers(issued[0])

        with self.service._lock:
            stored = self.receipts.stored_artifacts(log_id)
        down = False

        def tracker(messages):
            nonlocal down
            try:
                return self.ask(messages)
            except LLMUnavailable:
                down = True
                raise

        block_kinds = self.block_kinds_for(log_id) if self.block_kinds_for else None
        res, _ = build_receipt(
            self.service, log_id, self.sources_for(log_id), seal_hash=seal_hash,
            version=RECEIPT_V2, ask=tracker, stored=stored, stamp=self.stamp,
            block_kinds=block_kinds)
        if down:
            # Keep every answer already obtained, so the retry does not ask it again.
            store_artifacts(self.service, self.receipts, log_id, res.artifacts)
            raise RetryableJobError("llm_unavailable")
        res, _ = _persist(self.service, self.receipts, log_id, res, version=RECEIPT_V2)
        if res.receipt["questions_pending"]:
            record_alerts(self.service, log_id, [{
                "kind": "questions_incomplete", "log_id": log_id,
                "doc_rev": payload.get("doc_rev"),
                "seq": res.receipt["seal_seq"],
            }])
        return _identifiers(res)

    def _on_failed(self, db, job) -> None:
        """Queue hook: runs inside the queue's transaction, so no transaction here."""
        payload = job.payload or {}
        kind = "compile_failed" if job.kind == KIND_COMPILE else "questions_failed"
        insert_alert_in_tx(db, job.log_id, {
            "kind": kind, "log_id": job.log_id,
            "seq": payload.get("seal_seq"), "doc_rev": payload.get("doc_rev"),
            "job_id": job.id, "job_kind": job.kind, "attempts": job.attempts,
            "error_kind": job.error_kind,
        }, ts_seconds(self.service.clock()))

    # ---- execution ------------------------------------------------------------------------

    def handlers(self) -> dict:
        return {KIND_COMPILE: self.handle_compile, KIND_QUESTIONS: self.handle_questions}

    def runner(self) -> JobRunner:
        return JobRunner(self.queue, self.handlers(), worker_id=self.worker_id)

    def run_until_idle(self, max_jobs: int | None = None) -> int:
        return self.runner().run_until_idle(max_jobs=max_jobs)
