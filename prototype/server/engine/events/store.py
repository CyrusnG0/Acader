"""SQLite append-only store (event-log.md §3: one append at a time per log).

Append under BEGIN IMMEDIATE with a unique (log_id, seq), client_seq dedupe, and the post-seal
whitelist. Staging, the 5-minute merge, leases and snapshots (§5) live in app/events_service.py,
which calls `append_in_tx` so a flush and the events it produces commit together.
"""
import json
import sqlite3

from .chain import build_event, is_sealed

_DDL = """
CREATE TABLE IF NOT EXISTS events (
  log_id TEXT NOT NULL,
  seq INTEGER NOT NULL,
  client_seq INTEGER,
  type TEXT NOT NULL,
  body TEXT NOT NULL,
  PRIMARY KEY (log_id, seq)
);
CREATE UNIQUE INDEX IF NOT EXISTS events_client_seq ON events (log_id, client_seq)
  WHERE client_seq IS NOT NULL;
"""


class EventStore:
    def __init__(self, path: str = ":memory:"):
        self.db = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
        if path != ":memory:":
            self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript(_DDL)

    def events(self, log_id: str) -> list[dict]:
        rows = self.db.execute(
            "SELECT body FROM events WHERE log_id = ? ORDER BY seq", (log_id,)).fetchall()
        return [json.loads(r[0]) for r in rows]

    def head(self, log_id: str) -> dict | None:
        row = self.db.execute(
            "SELECT body FROM events WHERE log_id = ? ORDER BY seq DESC LIMIT 1",
            (log_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def close(self) -> None:
        self.db.close()

    def append_in_tx(self, log_id: str, *, type: str, actor: str, payload: dict, ts: str,
                     client_seq: int | None = None, doc_rev: int | None = None) -> dict:
        """Append inside a transaction the caller already holds (BEGIN IMMEDIATE). No commit."""
        if client_seq is not None:
            row = self.db.execute(
                "SELECT body FROM events WHERE log_id = ? AND client_seq = ?",
                (log_id, client_seq)).fetchone()
            if row:
                return json.loads(row[0])
        existing = self.events(log_id)
        head = existing[-1] if existing else None
        event = build_event(head, log_id, type=type, actor=actor, payload=payload, ts=ts,
                            client_seq=client_seq, doc_rev=doc_rev,
                            sealed=is_sealed(existing))
        self.db.execute(
            "INSERT INTO events (log_id, seq, client_seq, type, body) VALUES (?, ?, ?, ?, ?)",
            (log_id, event["seq"], client_seq, type,
             json.dumps(event, ensure_ascii=False, sort_keys=True)))
        return event

    def append(self, log_id: str, *, type: str, actor: str, payload: dict, ts: str,
               client_seq: int | None = None, doc_rev: int | None = None) -> dict:
        """Append one event and return it. A retried client_seq returns the stored event."""
        self.db.execute("BEGIN IMMEDIATE")
        try:
            event = self.append_in_tx(log_id, type=type, actor=actor, payload=payload, ts=ts,
                                      client_seq=client_seq, doc_rev=doc_rev)
            self.db.execute("COMMIT")
            return event
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
