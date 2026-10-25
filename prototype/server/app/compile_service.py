"""Compile a sealed log and record operator alerts. Never touches the event chain."""
from __future__ import annotations

import json

from app.events_service import EventService
from engine.events import canonical_json, ts_seconds
from engine.provenance import ProvenanceSources, compile_marks, operator_alerts
from engine.replay import SnapshotLoader

_DDL = """
CREATE TABLE IF NOT EXISTS operator_alerts (
  id INTEGER PRIMARY KEY AUTOINCREMENT, log_id TEXT NOT NULL, kind TEXT NOT NULL,
  doc_rev INTEGER NOT NULL, seq INTEGER NOT NULL, detail TEXT NOT NULL, created_at TEXT NOT NULL,
  UNIQUE (log_id, kind, seq));
"""


def load_snapshot_fn(service: EventService, log_id: str) -> SnapshotLoader:
    def load(ref: str) -> dict | None:
        if not isinstance(ref, str) or not ref.startswith("snap-"):
            return None
        tail = ref[len("snap-"):]
        if not tail.isdigit():
            return None
        with service._lock:
            row = service.db.execute("SELECT body FROM snapshots WHERE id = ? AND log_id = ?",
                                     (int(tail), log_id)).fetchone()
        return json.loads(row[0]) if row else None
    return load


def ensure_alerts_table(service: EventService) -> None:
    """Create the operator_alerts table. Must be called outside any transaction."""
    with service._lock:
        service.db.executescript(_DDL)


def insert_alert_in_tx(db, log_id: str, alert: dict, created_at: str) -> None:
    """Insert one operator alert inside the caller's transaction. No commit here."""
    db.execute(
        "INSERT OR IGNORE INTO operator_alerts "
        "(log_id, kind, doc_rev, seq, detail, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (log_id, alert["kind"], alert["doc_rev"], alert["seq"],
         canonical_json(alert).decode("utf-8"), created_at))


def record_alerts(service: EventService, log_id: str, alerts) -> None:
    """Record operator alerts in a transaction owned by this call (under the service lock)."""
    if not alerts:
        return
    with service._lock:
        service.db.execute("BEGIN IMMEDIATE")
        try:
            created = ts_seconds(service.clock())
            for a in alerts:
                insert_alert_in_tx(service.db, log_id, a, created)
            service.db.execute("COMMIT")
        except BaseException:
            service.db.execute("ROLLBACK")
            raise


def compile_log(service: EventService, log_id: str, sources: ProvenanceSources, *,
                seal_seq: int | None = None) -> dict:
    events = service.events(log_id)
    result = compile_marks(events, load_snapshot_fn(service, log_id), sources, seal_seq=seal_seq)
    alerts = operator_alerts(result, log_id)
    ensure_alerts_table(service)
    record_alerts(service, log_id, alerts)
    return result.to_json()


def list_alerts(service: EventService, log_id: str | None = None) -> list[dict]:
    ensure_alerts_table(service)
    with service._lock:
        sql = "SELECT id, log_id, kind, doc_rev, seq, detail, created_at FROM operator_alerts"
        args: tuple = ()
        if log_id is not None:
            sql += " WHERE log_id = ?"
            args = (log_id,)
        rows = service.db.execute(sql + " ORDER BY id", args).fetchall()
    return [{"id": r[0], "log_id": r[1], "kind": r[2], "doc_rev": r[3], "seq": r[4],
             "detail": json.loads(r[5]), "created_at": r[6]} for r in rows]
