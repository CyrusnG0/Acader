"""EventService: staging, the 5-minute merge, snapshots, leases, seal (event-log.md §3, §5, §6).

Privacy law: no client time and no typing rhythm is stored. Staging keeps only the 5-minute
window string the batch landed in, never the exact receipt time.
"""
import json
import re
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Callable

from engine.events import (INPUT_KINDS, CanonicalError, EventStore, SealedError, canonical_json,
                           count_words, is_sealed, merge_batches, ts_seconds, ts_window, verify)

LEASE_SECONDS = 90
HEARTBEAT_SECONDS = 30
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_FMT = "%Y-%m-%dT%H:%M:%SZ"

_DDL = """
CREATE TABLE IF NOT EXISTS staging (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  log_id TEXT NOT NULL,
  client_seq INTEGER NOT NULL,
  win TEXT NOT NULL,
  base_rev INTEGER NOT NULL,
  doc_rev INTEGER NOT NULL,
  body TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS log_state (
  log_id TEXT PRIMARY KEY,
  rev INTEGER NOT NULL,
  max_client_seq INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  log_id TEXT NOT NULL,
  doc_rev INTEGER NOT NULL,
  body TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS leases (
  log_id TEXT PRIMARY KEY,
  device_id TEXT NOT NULL,
  token TEXT NOT NULL,
  expires_at TEXT NOT NULL
);
"""


class LogNotFound(Exception):
    pass


class Conflict(Exception):
    def __init__(self, code: str, detail: dict | None = None):
        super().__init__(code)
        self.code = code
        self.detail = detail or {}


class Invalid(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _default_clock() -> datetime:
    return datetime.now(timezone.utc)


def _parse(ts: str) -> datetime:
    return datetime.strptime(ts, _FMT).replace(tzinfo=timezone.utc)


class EventService:
    def __init__(self, path: str = ":memory:", clock: Callable[[], datetime] | None = None):
        self.clock = clock or _default_clock
        self.store = EventStore(path)
        self.db = self.store.db
        self.db.executescript(_DDL)
        self._lock = threading.Lock()
        self._seal_hooks: list = []

    def close(self) -> None:
        self.store.close()

    def add_seal_hook(self, fn) -> None:
        """Register a hook called with (log_id, submit_event, db) inside the submit transaction.

        A hook exception rolls the whole submit back: no seal without its scheduled work.
        """
        self._seal_hooks.append(fn)

    # ---- helpers -------------------------------------------------------------------------

    @contextmanager
    def _tx(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.db.execute("COMMIT")
        except SealedError as e:
            self.db.execute("ROLLBACK")
            raise Conflict("sealed") from e
        except CanonicalError as e:
            self.db.execute("ROLLBACK")
            raise Invalid("not_canonical", str(e)) from e
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def _require_log(self, log_id: str) -> None:
        if self.store.head(log_id) is None:
            raise LogNotFound(log_id)

    def _state(self, log_id: str) -> tuple[int, int]:
        row = self.db.execute("SELECT rev, max_client_seq FROM log_state WHERE log_id = ?",
                              (log_id,)).fetchone()
        return (row[0], row[1]) if row else (0, 0)

    def _check_lease(self, log_id: str, token: str, now: datetime) -> None:
        row = self.db.execute("SELECT token, expires_at FROM leases WHERE log_id = ?",
                              (log_id,)).fetchone()
        if not row or row[0] != token or row[1] <= ts_seconds(now):
            raise Conflict("lease_lost")

    def _flush(self, log_id: str, *, force: bool, now: datetime | None = None) -> int:
        now = now or self.clock()
        current = ts_window(now)
        rows = self.db.execute(
            "SELECT id, win, doc_rev, body FROM staging WHERE log_id = ? ORDER BY id",
            (log_id,)).fetchall()
        groups: list[list[tuple]] = []
        for r in rows:
            if groups and groups[-1][0][1] == r[1]:
                groups[-1].append(r)
            else:
                groups.append([r])
        written = 0
        for g in groups:
            win = g[0][1]
            if not force and not win < current:
                continue
            payload = merge_batches([json.loads(r[3]) for r in g])
            self.store.append_in_tx(log_id, type="editor.batch", actor="student",
                                    payload=payload, ts=win, doc_rev=g[-1][2])
            self.db.execute(
                f"DELETE FROM staging WHERE id IN ({','.join('?' * len(g))})",
                [r[0] for r in g])
            written += 1
        return written

    def _store_snapshot(self, log_id: str, doc_rev: int, snapshot: dict) -> str:
        cur = self.db.execute("INSERT INTO snapshots (log_id, doc_rev, body) VALUES (?, ?, ?)",
                              (log_id, doc_rev, canonical_json(snapshot).decode("utf-8")))
        return f"snap-{cur.lastrowid}"

    @staticmethod
    def _check_hash(doc_hash: str) -> None:
        if not isinstance(doc_hash, str) or not _HEX64.match(doc_hash):
            raise Invalid("bad_batch", "doc_hash must be 64 lowercase hex characters.")

    # ---- logs ----------------------------------------------------------------------------

    def open_log(self, log_id: str | None, *, assignment_id: str, consent_version: int,
                 mapper_enabled: bool) -> dict:
        log_id = log_id or uuid.uuid4().hex
        with self._lock, self._tx():
            events = self.store.events(log_id)
            if events:
                return {"log_id": log_id, "event": events[0]}
            event = self.store.append_in_tx(
                log_id, type="log.open", actor="system",
                payload={"assignment_id": assignment_id, "consent_version": consent_version,
                         "mapper_enabled": mapper_enabled},
                ts=ts_seconds(self.clock()))
            self.db.execute("INSERT OR IGNORE INTO log_state (log_id, rev, max_client_seq) "
                            "VALUES (?, 0, 0)", (log_id,))
            return {"log_id": log_id, "event": event}

    def events(self, log_id: str) -> list[dict]:
        with self._lock:
            self._require_log(log_id)
            return self.store.events(log_id)

    # ---- merge ---------------------------------------------------------------------------

    def flush_due(self) -> int:
        with self._lock, self._tx():
            ids = [r[0] for r in self.db.execute("SELECT DISTINCT log_id FROM staging")]
            return sum(self._flush(i, force=False) for i in ids)

    def ack_batch(self, log_id: str, *, client_seq: int, base_rev: int, doc_rev: int,
                  steps: list[dict], input_kind: dict[str, int], lease_token: str) -> dict:
        with self._lock, self._tx():
            now = self.clock()
            self._require_log(log_id)
            self._check_lease(log_id, lease_token, now)
            if (not isinstance(steps, list) or not steps
                    or not all(isinstance(s, dict) for s in steps)):
                raise Invalid("bad_batch", "A batch needs a non-empty list of steps.")
            if doc_rev != base_rev + len(steps):
                raise Invalid("bad_batch", "doc_rev must equal base_rev plus the step count.")
            if not isinstance(input_kind, dict) or not all(
                    k in INPUT_KINDS and isinstance(v, int) and not isinstance(v, bool) and v >= 0
                    for k, v in input_kind.items()):
                raise Invalid("bad_batch", "input_kind has an unknown key or a bad count.")
            canonical_json({"steps": steps, "input_kind": input_kind})
            rev, max_seq = self._state(log_id)
            if client_seq <= max_seq:
                if doc_rev <= rev:
                    return {"acked": client_seq, "duplicate": True, "doc_rev": rev}
                raise Conflict("stale_client_seq", {"max_client_seq": max_seq})
            if is_sealed(self.store.events(log_id)):
                raise Conflict("sealed")
            if base_rev != rev:
                raise Conflict("rev_conflict", {"doc_rev": rev})
            self._flush(log_id, force=False, now=now)
            self.db.execute(
                "INSERT INTO staging (log_id, client_seq, win, base_rev, doc_rev, body) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (log_id, client_seq, ts_window(now), base_rev, doc_rev,
                 json.dumps({"steps": steps, "input_kind": input_kind}, sort_keys=True)))
            self.db.execute("UPDATE log_state SET rev = ?, max_client_seq = ? WHERE log_id = ?",
                            (doc_rev, client_seq, log_id))
            return {"acked": client_seq, "duplicate": False, "doc_rev": doc_rev}

    # ---- checkpoint / submit -------------------------------------------------------------

    def checkpoint(self, log_id: str, *, doc_rev: int, doc_hash: str, snapshot: dict,
                   lease_token: str) -> dict:
        with self._lock, self._tx():
            now = self.clock()
            self._require_log(log_id)
            self._check_lease(log_id, lease_token, now)
            events = self.store.events(log_id)
            if is_sealed(events):
                raise Conflict("sealed")
            rev, _ = self._state(log_id)
            if doc_rev != rev:
                raise Conflict("rev_conflict", {"doc_rev": rev})
            self._check_hash(doc_hash)
            canonical_json(snapshot)
            last = next((e for e in reversed(events) if e["type"] == "doc.checkpoint"), None)
            if last and (last["payload"]["doc_rev"] == doc_rev
                         or ts_window(_parse(last["ts"])) == ts_window(now)):
                self._flush(log_id, force=False, now=now)
                return {"skipped": True, "checkpoint": None}
            self._flush(log_id, force=True, now=now)
            ref = self._store_snapshot(log_id, doc_rev, snapshot)
            event = self.store.append_in_tx(
                log_id, type="doc.checkpoint", actor="system",
                payload={"doc_rev": doc_rev, "doc_hash": doc_hash, "snapshot_ref": ref},
                ts=ts_seconds(now), doc_rev=doc_rev)
            return {"skipped": False, "checkpoint": event}

    def submit(self, log_id: str, *, idempotency_key: str, doc_rev: int, doc_hash: str,
               snapshot: dict, lease_token: str) -> dict:
        with self._lock, self._tx():
            now = self.clock()
            self._require_log(log_id)
            events = self.store.events(log_id)
            submits = [e for e in events if e["type"] == "submit"]
            for e in submits:
                if e["payload"].get("idempotency_key") == idempotency_key:
                    for hook in self._seal_hooks:
                        hook(log_id, e, self.db)
                    return {"seal": e["hash"], "seal_seq": e["seq"],
                            "doc_rev": e["payload"]["doc_rev"], "replayed": True}
            self._check_lease(log_id, lease_token, now)
            if is_sealed(events):
                latest = submits[-1]
                if latest["payload"]["doc_rev"] == doc_rev:
                    raise Conflict("already_submitted",
                                   {"seal": latest["hash"], "seal_seq": latest["seq"]})
                raise Conflict("sealed")
            for e in submits:
                if e["payload"]["doc_rev"] == doc_rev:
                    raise Conflict("already_submitted", {"seal": e["hash"], "seal_seq": e["seq"]})
            rev, _ = self._state(log_id)
            if doc_rev != rev:
                raise Conflict("rev_conflict", {"doc_rev": rev})
            self._check_hash(doc_hash)
            canonical_json(snapshot)
            if count_words(snapshot) == 0:
                raise Invalid("empty_submit", "There is nothing to submit yet.")
            self._flush(log_id, force=True, now=now)
            ref = self._store_snapshot(log_id, doc_rev, snapshot)
            self.store.append_in_tx(
                log_id, type="doc.checkpoint", actor="system",
                payload={"doc_rev": doc_rev, "doc_hash": doc_hash, "snapshot_ref": ref},
                ts=ts_seconds(now), doc_rev=doc_rev)
            sub = self.store.append_in_tx(
                log_id, type="submit", actor="student",
                payload={"doc_rev": doc_rev, "doc_hash": doc_hash,
                         "idempotency_key": idempotency_key},
                ts=ts_seconds(now), doc_rev=doc_rev)
            for hook in self._seal_hooks:
                hook(log_id, sub, self.db)
            return {"seal": sub["hash"], "seal_seq": sub["seq"], "doc_rev": doc_rev,
                    "replayed": False}

    # ---- other events --------------------------------------------------------------------

    def append_event(self, log_id: str, *, type: str, actor: str, payload: dict,
                     client_seq: int | None = None, doc_rev: int | None = None) -> dict:
        with self._lock, self._tx():
            now = self.clock()
            self._require_log(log_id)
            self._flush(log_id, force=False, now=now)
            return self.store.append_in_tx(log_id, type=type, actor=actor, payload=payload,
                                           ts=ts_seconds(now), client_seq=client_seq,
                                           doc_rev=doc_rev)

    def open_resubmission(self, log_id: str, *, reason: str) -> dict:
        with self._lock, self._tx():
            now = self.clock()
            self._require_log(log_id)
            if not is_sealed(self.store.events(log_id)):
                raise Conflict("not_sealed")
            return self.store.append_in_tx(log_id, type="resubmit.open", actor="teacher",
                                           payload={"reason": reason}, ts=ts_seconds(now))

    def verify(self, log_id: str, seal: str | None = None) -> dict:
        with self._lock:
            self._require_log(log_id)
            events = self.store.events(log_id)
            if seal is None:
                subs = [e for e in events if e["type"] == "submit"]
                if not subs:
                    return {"ok": False, "problems": ["log is not sealed"], "seal_seq": None}
                seal = subs[-1]["hash"]
            r = verify(events, seal)
            return {"ok": r.ok, "problems": r.problems, "seal_seq": r.seal_seq}

    # ---- lease ---------------------------------------------------------------------------

    def acquire_lease(self, log_id: str, *, device_id: str, takeover: bool = False) -> dict:
        with self._lock, self._tx():
            now = self.clock()
            self._require_log(log_id)
            row = self.db.execute("SELECT device_id, expires_at FROM leases WHERE log_id = ?",
                                  (log_id,)).fetchone()
            if row and row[1] > ts_seconds(now) and row[0] != device_id and not takeover:
                raise Conflict("lease_held", {"device_id": row[0]})
            token = uuid.uuid4().hex
            exp = ts_seconds(now + timedelta(seconds=LEASE_SECONDS))
            self.db.execute("INSERT OR REPLACE INTO leases (log_id, device_id, token, expires_at) "
                            "VALUES (?, ?, ?, ?)", (log_id, device_id, token, exp))
            rev, max_seq = self._state(log_id)
            return {"token": token, "expires_at": exp, "heartbeat_seconds": HEARTBEAT_SECONDS,
                    "doc_rev": rev, "max_client_seq": max_seq}

    def heartbeat(self, log_id: str, *, token: str) -> dict:
        with self._lock, self._tx():
            now = self.clock()
            self._require_log(log_id)
            self._check_lease(log_id, token, now)
            exp = ts_seconds(now + timedelta(seconds=LEASE_SECONDS))
            self.db.execute("UPDATE leases SET expires_at = ? WHERE log_id = ?", (exp, log_id))
            return {"expires_at": exp}
