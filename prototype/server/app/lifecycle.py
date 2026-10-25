"""Receipt release and transactional withdrawal (receipt.md §7; architecture.md §3; D10).

Release rule
------------
A sealed submission is released to the teacher at the latest of

* the assignment deadline,
* submit + 24 hours,
* the moment its questions are ready,

and never later than ``max(deadline, submit + 24h) + 48h``. At that cap the newest stored
receipt is released even though its questions are still pending, and one ``release_cap``
operator alert is recorded. Questions that arrive after the cap stay in a later receipt
version; :meth:`ReceiptLifecycle.teacher_view` returns them as ``late_questions`` marked
``added_after_release``. The released receipt bytes themselves never change.

Before release the teacher view carries only ``status: compiling`` and the guaranteed
``ready_by`` time. No receipt, summary, bands, question text or receipt identifier is
returned.

Release is not an event: the post-seal whitelist (event-log.md §6) does not include one, so
release state lives in the lifecycle table. The receipt stays sealed and verifiable.

Withdrawal
----------
:meth:`ReceiptLifecycle.withdraw` runs one caller-owned ``BEGIN IMMEDIATE`` transaction that
appends ``record.withdrawn``, cancels every queued and running job for the log, deletes the
log's unreleased receipts and stored outputs, writes the teacher-side tombstone and marks the
release records. A running worker checks :mod:`app.withdrawal` inside its own publication
transaction, so a receipt or artifact cannot be written after the withdrawal commits.
Submitted work (the event chain and snapshots) is never deleted, and withdrawal after release
is refused with :class:`AfterRelease` rather than silently converted.

Every read and write is scoped by ``log_id`` and by an explicit :class:`Identity`
(tenant + role + owner). Unknown records, unowned records and wrong roles fail closed with
:class:`AccessDenied`. These identities are supplied by the caller; this module does not
authenticate anyone.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable

from app.compile_service import ensure_alerts_table, insert_alert_in_tx
from app.events_service import EventService
from app.jobs import JobQueue, PermanentJobError, PRIORITY_NORMAL
from app.receipt_store import ReceiptStore
from app.withdrawal import is_withdrawn_in_tx
from engine.events import ts_seconds

KIND_RELEASE = "receipt.release"
PHASE_BASE = "base"
PHASE_CAP = "cap"
PHASE_QUESTIONS = "questions"

RELEASE_DELAY_HOURS = 24
RELEASE_CAP_HOURS = 48

_FMT = "%Y-%m-%dT%H:%M:%SZ"

_DDL = """
CREATE TABLE IF NOT EXISTS release_records (
  log_id TEXT NOT NULL,
  seal_hash TEXT NOT NULL,
  tenant_id TEXT,
  owner_id TEXT,
  submit_at TEXT NOT NULL,
  deadline_at TEXT NOT NULL,
  base_at TEXT NOT NULL,
  cap_at TEXT NOT NULL,
  seal_seq INTEGER NOT NULL,
  doc_rev INTEGER NOT NULL,
  released_at TEXT,
  released_version INTEGER,
  release_kind TEXT,
  withdrawn_at TEXT,
  PRIMARY KEY (log_id, seal_hash)
);
CREATE TABLE IF NOT EXISTS record_tombstones (
  log_id TEXT PRIMARY KEY,
  seal_hash TEXT NOT NULL,
  tenant_id TEXT,
  owner_id TEXT,
  withdrawn_at TEXT NOT NULL,
  reason TEXT
);
"""

_RECORD_COLUMNS = ("log_id, seal_hash, tenant_id, owner_id, submit_at, deadline_at, base_at, "
                   "cap_at, seal_seq, doc_rev, released_at, released_version, release_kind, "
                   "withdrawn_at")

_TOMBSTONE_COLUMNS = "log_id, seal_hash, tenant_id, owner_id, withdrawn_at, reason"


class LifecycleError(Exception):
    """Base class for lifecycle refusals."""


class AccessDenied(LifecycleError):
    """The identity or the log scope does not permit this operation (fail closed)."""


class AfterRelease(LifecycleError):
    """The record was already released; withdrawal is a different, unbuilt operation."""


class LifecycleConflict(LifecycleError):
    """The requested lifecycle transition is not valid for the stored state."""


@dataclass(frozen=True)
class Identity:
    """A caller-supplied, already-authenticated identity (synthetic in tests)."""
    tenant_id: str
    role: str
    owner_id: str | None = None


@dataclass(frozen=True)
class RecordScope:
    """Who owns one record. Supplied at submit by the caller's roster/assignment layer."""
    tenant_id: str
    owner_id: str


def release_key(log_id: str, seal_hash: str, phase: str) -> str:
    return f"{KIND_RELEASE}:{log_id}:{seal_hash}:{phase}"


def _parse(ts: str) -> datetime:
    return datetime.strptime(ts, _FMT).replace(tzinfo=timezone.utc)


def _aware(value: datetime, what: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise LifecycleConflict(f"{what} must be a timezone-aware datetime")
    return value


def _identity(value) -> Identity:
    if not isinstance(value, Identity):
        raise AccessDenied("an explicit identity is required")
    if not isinstance(value.tenant_id, str) or not value.tenant_id:
        raise AccessDenied("the identity has no tenant")
    if not isinstance(value.role, str) or not value.role:
        raise AccessDenied("the identity has no role")
    if value.owner_id is not None and (not isinstance(value.owner_id, str)
                                       or not value.owner_id):
        raise AccessDenied("the identity owner is invalid")
    return value


def _scope(value) -> RecordScope | None:
    if value is None:
        return None
    if not isinstance(value, RecordScope):
        raise LifecycleConflict("scope_for must return RecordScope or None")
    if not isinstance(value.tenant_id, str) or not value.tenant_id:
        raise LifecycleConflict("a record scope needs a tenant")
    if not isinstance(value.owner_id, str) or not value.owner_id:
        raise LifecycleConflict("a record scope needs an owner")
    return value


class ReceiptLifecycle:
    """Release scheduling and transactional withdrawal for sealed logs."""

    def __init__(self, service: EventService, *, queue: JobQueue,
                 receipts: ReceiptStore | None = None,
                 deadline_for: Callable[[str], datetime | None] | None = None,
                 scope_for: Callable[[str], RecordScope | None] | None = None):
        if queue.db is not service.db:
            raise ValueError("the release queue must share the event connection")
        if queue._lock is not service._lock:
            raise ValueError("the release queue must share the event lock")
        self.service = service
        self.queue = queue
        self.receipts = receipts or ReceiptStore(service.db)
        if self.receipts.db is not service.db:
            raise ValueError("the receipt store must share the event connection")
        self.deadline_for = deadline_for or (lambda log_id: None)
        self.scope_for = scope_for or (lambda log_id: None)
        self.db = service.db
        ensure_alerts_table(service)
        self.db.executescript(_DDL)
        service.add_seal_hook(self.on_seal)

    # ---- rows ----------------------------------------------------------------------------

    @staticmethod
    def _record(row) -> dict:
        keys = ("log_id", "seal_hash", "tenant_id", "owner_id", "submit_at", "deadline_at",
                "base_at", "cap_at", "seal_seq", "doc_rev", "released_at",
                "released_version", "release_kind", "withdrawn_at")
        return dict(zip(keys, row))

    @staticmethod
    def _tombstone_row(row) -> dict:
        keys = ("log_id", "seal_hash", "tenant_id", "owner_id", "withdrawn_at", "reason")
        return dict(zip(keys, row))

    def _release_row(self, log_id: str, seal_hash: str) -> dict | None:
        row = self.db.execute(
            f"SELECT {_RECORD_COLUMNS} FROM release_records "
            "WHERE log_id = ? AND seal_hash = ?", (log_id, seal_hash)).fetchone()
        return self._record(row) if row else None

    def _latest_release_row(self, log_id: str) -> dict | None:
        row = self.db.execute(
            f"SELECT {_RECORD_COLUMNS} FROM release_records WHERE log_id = ? "
            "ORDER BY seal_seq DESC LIMIT 1", (log_id,)).fetchone()
        return self._record(row) if row else None

    def _tombstone(self, log_id: str) -> dict | None:
        row = self.db.execute(
            f"SELECT {_TOMBSTONE_COLUMNS} FROM record_tombstones WHERE log_id = ?",
            (log_id,)).fetchone()
        return self._tombstone_row(row) if row else None

    def _latest_receipt(self, log_id: str, seal_hash: str) -> tuple[int, dict] | None:
        row = self.db.execute(
            "SELECT version, body FROM receipts WHERE log_id = ? AND seal_hash = ? "
            "ORDER BY version DESC LIMIT 1", (log_id, seal_hash)).fetchone()
        if row is None:
            return None
        return row[0], json.loads(bytes(row[1]).decode("utf-8"))

    def _questions_ready(self, log_id: str, seal_hash: str) -> bool:
        latest = self._latest_receipt(log_id, seal_hash)
        if latest is None:
            return False
        return not bool(latest[1].get("questions_pending"))

    # ---- scheduling -----------------------------------------------------------------------

    def on_seal(self, log_id: str, submit_event: dict, db: sqlite3.Connection) -> None:
        """Record the release window and enqueue base/cap checks inside the submit transaction."""
        submit_at = _parse(submit_event["ts"])
        deadline = self.deadline_for(log_id)
        deadline = submit_at if deadline is None else _aware(deadline, "the deadline")
        base = max(deadline, submit_at + timedelta(hours=RELEASE_DELAY_HOURS))
        cap = base + timedelta(hours=RELEASE_CAP_HOURS)
        scope = _scope(self.scope_for(log_id))
        tenant = scope.tenant_id if scope else None
        owner = scope.owner_id if scope else None
        payload = {"seal_hash": submit_event["hash"], "seal_seq": submit_event["seq"],
                   "doc_rev": submit_event["payload"]["doc_rev"]}
        db.execute(
            "INSERT OR IGNORE INTO release_records "
            "(log_id, seal_hash, tenant_id, owner_id, submit_at, deadline_at, base_at, cap_at, "
            "seal_seq, doc_rev) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (log_id, submit_event["hash"], tenant, owner, ts_seconds(submit_at),
             ts_seconds(deadline), ts_seconds(base), ts_seconds(cap),
             submit_event["seq"], submit_event["payload"]["doc_rev"]))
        for phase, when in ((PHASE_BASE, base), (PHASE_CAP, cap)):
            self.queue.enqueue(
                KIND_RELEASE, idempotency_key=release_key(log_id, submit_event["hash"], phase),
                log_id=log_id, priority=PRIORITY_NORMAL, backend=None,
                payload={**payload, "phase": phase}, run_after=when, conn=db)

    def questions_ready(self, log_id: str, seal_hash: str) -> None:
        """After a complete receipt version is stored, check release without waiting for the cap.

        Notification failure must not fail receipt issuance: the cap job still guarantees a
        release. This runs after the issuance transaction has committed.
        """
        with self.service._lock:
            record = self._release_row(log_id, seal_hash)
        if record is None or record["withdrawn_at"] is not None:
            return
        now = self.service.clock()
        try:
            self.queue.enqueue(
                KIND_RELEASE, idempotency_key=release_key(log_id, seal_hash, PHASE_QUESTIONS),
                log_id=log_id, priority=PRIORITY_NORMAL, backend=None,
                payload={"seal_hash": seal_hash, "seal_seq": record["seal_seq"],
                         "doc_rev": record["doc_rev"], "phase": PHASE_QUESTIONS},
                run_after=max(now, _parse(record["base_at"])))
        except Exception:
            return  # cap remains the guarantee; never fail the compile that stored the receipt

    def handlers(self) -> dict:
        return {KIND_RELEASE: self.handle_release}

    # ---- release --------------------------------------------------------------------------

    def handle_release(self, job) -> dict:
        """Publish the release when due. Never writes receipt bytes or the chain."""
        payload = job.payload or {}
        log_id, seal_hash = job.log_id, payload.get("seal_hash")
        if not isinstance(log_id, str) or not isinstance(seal_hash, str):
            raise PermanentJobError("release_record_missing")
        with self.service._lock, self.service._tx():
            return self._release_in_tx(log_id, seal_hash)

    def _release_in_tx(self, log_id: str, seal_hash: str) -> dict:
        record = self._release_row(log_id, seal_hash)
        if record is None:
            raise PermanentJobError("release_record_missing")
        if record["withdrawn_at"] is not None or is_withdrawn_in_tx(self.db, log_id):
            return {"status": "withdrawn"}
        if record["released_at"] is not None:
            return {"status": "released", "released_at": record["released_at"],
                    "released_version": record["released_version"],
                    "release_kind": record["release_kind"]}
        now = self.service.clock()
        base, cap = _parse(record["base_at"]), _parse(record["cap_at"])
        if now < base:
            return {"status": "waiting"}
        ready = self._questions_ready(log_id, seal_hash)
        if not ready and now < cap:
            return {"status": "waiting"}
        latest = self._latest_receipt(log_id, seal_hash)
        if latest is None:
            # Nothing was ever compiled. Never invent a receipt; tell the operator and keep
            # the record unreleased so a later compile can still be released.
            insert_alert_in_tx(self.db, log_id, {
                "kind": "release_no_receipt", "log_id": log_id,
                "seq": record["seal_seq"], "doc_rev": record["doc_rev"],
            }, ts_seconds(now))
            return {"status": "no_receipt"}
        version, receipt = latest
        kind = "ready" if ready else "cap"
        released_at = ts_seconds(now)
        cur = self.db.execute(
            "UPDATE release_records SET released_at = ?, released_version = ?, release_kind = ? "
            "WHERE log_id = ? AND seal_hash = ? AND released_at IS NULL",
            (released_at, version, kind, log_id, seal_hash))
        if cur.rowcount == 0:  # a concurrent release won; return its state
            again = self._release_row(log_id, seal_hash)
            return {"status": "released", "released_at": again["released_at"],
                    "released_version": again["released_version"],
                    "release_kind": again["release_kind"]}
        if kind == "cap" and receipt.get("questions_pending"):
            insert_alert_in_tx(self.db, log_id, {
                "kind": "release_cap", "log_id": log_id,
                "seq": record["seal_seq"], "doc_rev": record["doc_rev"],
                "receipt_id": receipt.get("receipt_id"), "version": version,
                "questions_pending": True,
            }, released_at)
        return {"status": "released", "released_at": released_at,
                "released_version": version, "release_kind": kind}

    # ---- reads ----------------------------------------------------------------------------

    @staticmethod
    def _require_teacher(identity: Identity, tenant_id: str | None) -> None:
        if identity.role != "teacher":
            raise AccessDenied("only a teacher can read the teacher view")
        if not tenant_id or identity.tenant_id != tenant_id:
            raise AccessDenied("this identity cannot read that record")

    def teacher_view(self, identity, log_id: str) -> dict:
        """The teacher-facing state. Before release it carries no receipt contents."""
        identity = _identity(identity)
        with self.service._lock:
            tomb = self._tombstone(log_id)
            if tomb is not None:
                self._require_teacher(identity, tomb["tenant_id"])
                return {"status": "record_removed", "withdrawn_at": tomb["withdrawn_at"]}
            record = self._latest_release_row(log_id)
            if (record is None or record["withdrawn_at"] is not None
                    or is_withdrawn_in_tx(self.db, log_id)):
                raise AccessDenied("this identity cannot read that record")
            self._require_teacher(identity, record["tenant_id"])
            if record["released_at"] is None:
                return {"status": "compiling", "ready_by": record["cap_at"]}
            stored = self.receipts.get(log_id, seal_hash=record["seal_hash"],
                                       version=record["released_version"])
            if stored is None:
                raise AccessDenied("the released receipt is not available")
            latest = self._latest_receipt(log_id, record["seal_hash"])
            late: list[dict] = []
            if latest is not None and latest[0] > record["released_version"]:
                late = [{**q, "added_after_release": True}
                        for q in latest[1].get("questions", []) if q.get("q")]
            pending = latest[1].get("questions_pending") if latest else \
                stored.receipt.get("questions_pending")
            return {
                "status": "questions_pending" if pending else "ready",
                "released_at": record["released_at"],
                "release_kind": record["release_kind"],
                "receipt": stored.receipt,
                "late_questions": late,
            }

    def is_withdrawn(self, log_id: str) -> bool:
        """True when this log has a withdrawal event (used outside a transaction)."""
        with self.service._lock:
            return self._tombstone(log_id) is not None or is_withdrawn_in_tx(self.db, log_id)

    # ---- withdrawal -----------------------------------------------------------------------

    def withdraw(self, identity, log_id: str, *, reason: str | None = None) -> dict:
        """Cancel work and remove the unreleased record atomically (D10).

        The caller owns no transaction. A running worker's publication is blocked by
        :func:`app.withdrawal.assert_not_withdrawn_in_tx`, which it calls inside its own
        transaction.
        """
        identity = _identity(identity)
        if identity.role != "student" or not identity.owner_id:
            raise AccessDenied("only the student who owns the record can remove it")
        if reason is not None and not isinstance(reason, str):
            raise LifecycleConflict("reason must be text")
        with self.service._lock, self.service._tx():
            tomb = self._tombstone(log_id)
            record = self._latest_release_row(log_id)
            scope = tomb or record
            if scope is None:
                raise AccessDenied("this identity cannot remove that record")
            if identity.tenant_id != scope["tenant_id"] or identity.owner_id != scope["owner_id"]:
                raise AccessDenied("this identity cannot remove that record")
            if tomb is not None:
                event = self._withdrawal_event(log_id)
                self.queue.cancel_by_log(log_id, reason="record.withdrawn", conn=self.db)
                self.receipts.delete_log_in_tx(log_id)
                return {"status": "record_removed", "withdrawn_at": tomb["withdrawn_at"],
                        "replayed": True, "event": event}
            released = self.db.execute(
                "SELECT 1 FROM release_records WHERE log_id = ? AND released_at IS NOT NULL "
                "LIMIT 1", (log_id,)).fetchone()
            if released is not None:
                raise AfterRelease("this record was already released; removal is a "
                                   "different operation")
            now_ts = ts_seconds(self.service.clock())
            event = self.service.store.append_in_tx(
                log_id, type="record.withdrawn", actor="student",
                payload={"reason": reason} if reason else {}, ts=now_ts,
                doc_rev=scope.get("doc_rev"))
            self.queue.cancel_by_log(log_id, reason="record.withdrawn", conn=self.db)
            self.receipts.delete_log_in_tx(log_id)
            self.db.execute(
                "INSERT INTO record_tombstones "
                "(log_id, seal_hash, tenant_id, owner_id, withdrawn_at, reason) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (log_id, scope["seal_hash"], scope["tenant_id"], scope["owner_id"],
                 now_ts, reason))
            self.db.execute(
                "UPDATE release_records SET withdrawn_at = ? "
                "WHERE log_id = ? AND withdrawn_at IS NULL", (now_ts, log_id))
            return {"status": "record_removed", "withdrawn_at": now_ts,
                    "replayed": False, "event": event}

    def _withdrawal_event(self, log_id: str) -> dict | None:
        row = self.db.execute(
            "SELECT body FROM events WHERE log_id = ? AND type = 'record.withdrawn' "
            "ORDER BY seq DESC LIMIT 1", (log_id,)).fetchone()
        return json.loads(row[0]) if row else None
