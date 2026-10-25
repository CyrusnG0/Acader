"""Durable receipts and compile artifacts (D31; receipt.md §6; event-log.md §6).

The chain stores `receipt.issued` as an event. The receipt bytes themselves, and every AI
output behind them, live in the two tables below, on the same SQLite connection and in the same
transactions as the event log. A stored receipt is immutable: `(log_id, seal_hash, version)`
names one receipt and its hash is checked against its canonical bytes on every read.

Transaction conventions match `app/events_service.py`:
- `store_in_tx`, `delete_log_in_tx` and `get`/`artifacts` do not begin or commit a transaction.
  An event append and the rows it describes must share the caller's `BEGIN IMMEDIATE`.
- `store` and `delete_log` are convenience wrappers that open their own transaction.
- No transaction is held while the compiler calls a model; `issue_receipt` compiles first,
  then writes the receipt, its artifacts and `receipt.issued` together.

Reads and deletes are always scoped by `log_id`, so one student's stored outputs can never be
read for, or removed with, another's. `delete_log_in_tx` is the hook for later withdrawal
(T-021): it can run inside the caller's transaction that also appends `record.withdrawn`.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass

from engine.events import CanonicalError, VerifyResult, canonical_json, sha256_hex, verify

_DDL = (
    """
    CREATE TABLE IF NOT EXISTS receipts (
      log_id TEXT NOT NULL,
      seal_hash TEXT NOT NULL,
      version INTEGER NOT NULL,
      receipt_id TEXT NOT NULL,
      seal_seq INTEGER NOT NULL,
      receipt_hash TEXT NOT NULL,
      body BLOB NOT NULL,
      PRIMARY KEY (log_id, seal_hash, version)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS receipt_artifacts (
      log_id TEXT NOT NULL,
      artifact_id TEXT NOT NULL,
      task TEXT NOT NULL,
      prompt_hash TEXT NOT NULL,
      body TEXT NOT NULL,
      hash TEXT NOT NULL,
      PRIMARY KEY (log_id, artifact_id)
    )
    """,
)

_RECEIPT_COLUMNS = "log_id, seal_hash, version, receipt_id, seal_seq, receipt_hash, body"


class ReceiptStoreError(Exception):
    """Base class for storage failures."""


class ReceiptConflict(ReceiptStoreError):
    """A different receipt or artifact is already stored under the same key."""


class CorruptReceipt(ReceiptStoreError):
    """Stored receipt bytes do not reproduce their recorded hash."""


class CorruptArtifact(ReceiptStoreError):
    """A stored artifact body does not reproduce its recorded hash."""


@dataclass(frozen=True)
class StoredReceipt:
    log_id: str
    seal_hash: str
    version: int
    receipt_id: str
    seal_seq: int
    receipt_hash: str
    body: bytes

    @property
    def receipt(self) -> dict:
        return json.loads(self.body.decode("utf-8"))

    @property
    def canonical_bytes(self) -> bytes:
        return self.body


def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def artifact_row(artifact_id: str, artifact: Mapping) -> tuple:
    """Validate one artifact and return the row to insert. Raises CorruptArtifact."""
    if not isinstance(artifact, Mapping):
        raise CorruptArtifact(f"artifact {artifact_id}: not an object")
    if artifact.get("artifact_id", artifact_id) != artifact_id:
        raise CorruptArtifact(f"artifact {artifact_id}: artifact_id does not match its key")
    task, prompt_hash = artifact.get("task"), artifact.get("prompt_hash")
    body, digest = artifact.get("body"), artifact.get("hash")
    if not all(isinstance(v, str) for v in (task, prompt_hash, body, digest)):
        raise CorruptArtifact(f"artifact {artifact_id}: task, prompt_hash, body and hash "
                              "must be strings")
    if sha256_hex(body.encode("utf-8")) != digest:
        raise CorruptArtifact(f"artifact {artifact_id}: body does not match its hash")
    return artifact_id, task, prompt_hash, body, digest


class ReceiptStore:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        # Individual statements, not executescript(): executescript() commits first, which
        # would break a caller already holding BEGIN IMMEDIATE.
        for statement in _DDL:
            self.db.execute(statement)

    # ---- rows -----------------------------------------------------------------------------

    @staticmethod
    def _stored(row) -> StoredReceipt:
        return StoredReceipt(log_id=row[0], seal_hash=row[1], version=row[2],
                             receipt_id=row[3], seal_seq=row[4], receipt_hash=row[5],
                             body=bytes(row[6]))

    @staticmethod
    def _check_receipt(stored: StoredReceipt) -> None:
        body = stored.body
        try:
            parsed = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as exc:
            raise CorruptReceipt(f"stored receipt {stored.receipt_id}: not valid JSON") from exc
        try:
            if canonical_json(parsed) != body:
                raise CorruptReceipt(f"stored receipt {stored.receipt_id}: bytes are not "
                                     "canonical")
        except CanonicalError as exc:
            raise CorruptReceipt(f"stored receipt {stored.receipt_id}: {exc}") from exc
        if sha256_hex(body) != stored.receipt_hash:
            raise CorruptReceipt(f"stored receipt {stored.receipt_id}: bytes do not match "
                                 "the recorded hash")

    @staticmethod
    def _artifact(row) -> dict:
        return {"artifact_id": row[0], "task": row[1], "prompt_hash": row[2],
                "body": row[3], "hash": row[4]}

    # ---- reads ----------------------------------------------------------------------------

    def get(self, log_id: str, *, seal_hash: str | None = None,
            version: int = 1) -> StoredReceipt | None:
        """One receipt for this log. With no seal_hash, the highest seal for the version."""
        sql = f"SELECT {_RECEIPT_COLUMNS} FROM receipts WHERE log_id = ? AND version = ?"
        args: list = [log_id, version]
        if seal_hash is None:
            sql += " ORDER BY seal_seq DESC LIMIT 1"
        else:
            sql += " AND seal_hash = ? LIMIT 1"
            args.append(seal_hash)
        row = self.db.execute(sql, args).fetchone()
        if row is None:
            return None
        stored = self._stored(row)
        self._check_receipt(stored)
        return stored

    def latest(self, log_id: str) -> StoredReceipt | None:
        """The stored receipt for this log with the highest version and seal."""
        row = self.db.execute(
            f"SELECT {_RECEIPT_COLUMNS} FROM receipts WHERE log_id = ? "
            "ORDER BY version DESC, seal_seq DESC LIMIT 1", (log_id,)).fetchone()
        if row is None:
            return None
        stored = self._stored(row)
        self._check_receipt(stored)
        return stored

    def artifacts(self, log_id: str) -> dict[str, dict]:
        """Every artifact row for this log, exactly as stored (hashes not rechecked)."""
        rows = self.db.execute(
            f"SELECT artifact_id, task, prompt_hash, body, hash FROM receipt_artifacts "
            "WHERE log_id = ? ORDER BY artifact_id", (log_id,)).fetchall()
        return {r[0]: self._artifact(r) for r in rows}

    def stored_artifacts(self, log_id: str) -> dict[str, dict]:
        """Artifacts for this log whose body still matches its hash.

        Raises CorruptArtifact rather than silently rebuilding with a damaged or missing
        output; a recompile must never fall back to a model call because a row was bad.
        """
        out: dict[str, dict] = {}
        for aid, artifact in self.artifacts(log_id).items():
            artifact_row(aid, artifact)
            out[aid] = artifact
        return out

    def _events(self, log_id: str) -> list[dict]:
        rows = self.db.execute(
            "SELECT body FROM events WHERE log_id = ? ORDER BY seq", (log_id,)).fetchall()
        return [json.loads(r[0]) for r in rows]

    def verify(self, log_id: str, *, seal_hash: str | None = None, version: int = 1,
               extra_artifacts: Mapping | None = None) -> VerifyResult:
        """Check the chain, the stored receipt and every artifact it (or the log) cites.

        `extra_artifacts` lets a caller supply outputs stored by another component (for
        example a mapper artifact cited by `map.finding`); they are checked the same way.
        Missing or corrupt stored rows are reported, never ignored.
        """
        try:
            stored = self.get(log_id, seal_hash=seal_hash, version=version)
        except CorruptReceipt as exc:
            return VerifyResult(ok=False, problems=[str(exc)], seal_seq=None)
        if stored is None:
            return VerifyResult(ok=False, problems=["no stored receipt for this log"],
                                seal_seq=None)
        events = self._events(log_id)
        artifacts = self.artifacts(log_id)
        if extra_artifacts:
            artifacts = {**artifacts, **extra_artifacts}
        return verify(events, stored.seal_hash, receipt=stored.receipt, artifacts=artifacts)

    # ---- writes ---------------------------------------------------------------------------

    def store_in_tx(self, log_id: str, *, receipt: Mapping, receipt_hash: str | None = None,
                    artifacts: Mapping[str, Mapping] | None = None,
                    extra_artifacts: Mapping[str, Mapping] | None = None,
                    seal_hash: str | None = None, seal_seq: int | None = None,
                    version: int | None = None) -> bool:
        """Store one receipt and its artifacts inside the caller's transaction.

        Returns True when the receipt row is new, False when an identical one was already
        stored (a retry). Raises ReceiptConflict if a different receipt would replace it and
        CorruptArtifact if an artifact body does not match its hash. No commit here.
        """
        if not isinstance(receipt, Mapping):
            raise ReceiptStoreError("receipt must be an object")
        if receipt.get("log_id") != log_id:
            raise ReceiptConflict("receipt belongs to a different log")
        receipt_id = receipt.get("receipt_id")
        receipt_version = receipt.get("version")
        receipt_seal = receipt.get("seal_hash")
        receipt_seq = receipt.get("seal_seq")
        if not isinstance(receipt_id, str) or not receipt_id:
            raise ReceiptStoreError("receipt has no receipt_id")
        if not _is_int(receipt_version) or receipt_version < 1:
            raise ReceiptStoreError("receipt version must be a positive integer")
        if not isinstance(receipt_seal, str) or not receipt_seal:
            raise ReceiptStoreError("receipt has no seal_hash")
        if not _is_int(receipt_seq) or receipt_seq < 0:
            raise ReceiptStoreError("receipt has no seal_seq")
        if version is not None and version != receipt_version:
            raise ReceiptConflict("version differs from the receipt")
        if seal_hash is not None and seal_hash != receipt_seal:
            raise ReceiptConflict("seal_hash differs from the receipt")
        if seal_seq is not None and seal_seq != receipt_seq:
            raise ReceiptConflict("seal_seq differs from the receipt")
        try:
            body = canonical_json(receipt)  # a float or a non-JSON value cannot be stored
        except CanonicalError as exc:
            raise ReceiptStoreError(f"receipt is not canonical JSON: {exc}") from exc
        digest = sha256_hex(body)
        if receipt_hash is not None and receipt_hash != digest:
            raise ReceiptConflict("receipt_hash does not match the receipt bytes")

        row = self.db.execute(
            "SELECT receipt_hash, body FROM receipts "
            "WHERE log_id = ? AND seal_hash = ? AND version = ?",
            (log_id, receipt_seal, receipt_version)).fetchone()
        if row is not None:
            if bytes(row[1]) == body and row[0] == digest:
                return False
            raise ReceiptConflict("another receipt is already stored for this seal and version")
        self.db.execute(
            "INSERT INTO receipts (log_id, seal_hash, version, receipt_id, seal_seq, "
            "receipt_hash, body) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (log_id, receipt_seal, receipt_version, receipt_id, receipt_seq, digest, body))

        merged: dict[str, Mapping] = {}
        for source in (artifacts or {}, extra_artifacts or {}):
            for aid, artifact in source.items():
                if aid in merged and merged[aid] != artifact:
                    raise ReceiptConflict(f"artifact {aid} is given twice with different bodies")
                merged[aid] = artifact
        for aid, artifact in merged.items():
            row_data = artifact_row(aid, artifact)
            row = self.db.execute(
                "SELECT task, prompt_hash, body, hash FROM receipt_artifacts "
                "WHERE log_id = ? AND artifact_id = ?", (log_id, aid)).fetchone()
            if row is not None:
                if tuple(row) != row_data[1:]:
                    raise ReceiptConflict(f"another artifact {aid} is already stored")
                continue
            self.db.execute(
                "INSERT INTO receipt_artifacts (log_id, artifact_id, task, prompt_hash, "
                "body, hash) VALUES (?, ?, ?, ?, ?, ?)", (log_id, *row_data))
        return True

    def store(self, log_id: str, **kwargs) -> bool:
        """`store_in_tx` in a transaction owned by this call."""
        self.db.execute("BEGIN IMMEDIATE")
        try:
            created = self.store_in_tx(log_id, **kwargs)
            self.db.execute("COMMIT")
            return created
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    # ---- deletion -------------------------------------------------------------------------

    def delete_log_in_tx(self, log_id: str) -> int:
        """Delete this log's receipts and artifacts inside the caller's transaction.

        No commit here, so a withdrawal event and the deletion can commit together. The
        event chain itself is never touched.
        """
        deleted = 0
        for table in ("receipts", "receipt_artifacts"):
            cur = self.db.execute(f"DELETE FROM {table} WHERE log_id = ?", (log_id,))
            deleted += cur.rowcount
        return deleted

    def delete_log(self, log_id: str) -> int:
        """`delete_log_in_tx` in a transaction owned by this call."""
        self.db.execute("BEGIN IMMEDIATE")
        try:
            deleted = self.delete_log_in_tx(log_id)
            self.db.execute("COMMIT")
            return deleted
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
