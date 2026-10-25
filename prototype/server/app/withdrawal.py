"""Withdrawal state checks used inside a publication transaction (eng review v2 D10).

A withdrawal is atomic: `record.withdrawn` and the teacher-side tombstone commit together
(app/lifecycle.py). A worker that is already running when the student withdraws must not
publish a receipt or stored output afterwards. Every publication path therefore calls
:func:`assert_not_withdrawn_in_tx` *inside* its own write transaction, before it writes.

The check reads the chain event, which is canonical and exists in every database. It is used
only inside a caller-owned ``BEGIN IMMEDIATE`` transaction, so a concurrent withdrawal either
commits before the read (the publication is refused) or waits until the publication commits.
"""
from __future__ import annotations

import sqlite3


class RecordWithdrawn(Exception):
    """Publication refused: this record was withdrawn before release.

    T-021 raises this from a running job's publication transaction. The queue has already
    fenced the job, so the runner discards the outcome; no receipt, artifact or release state
    is written.
    """


def is_withdrawn_in_tx(db: sqlite3.Connection, log_id: str) -> bool:
    """True when this log's chain already holds a ``record.withdrawn`` event."""
    row = db.execute(
        "SELECT 1 FROM events WHERE log_id = ? AND type = 'record.withdrawn' LIMIT 1",
        (log_id,)).fetchone()
    return row is not None


def assert_not_withdrawn_in_tx(db: sqlite3.Connection, log_id: str) -> None:
    """Raise :class:`RecordWithdrawn` when the caller must not publish for this log."""
    if is_withdrawn_in_tx(db, log_id):
        raise RecordWithdrawn(f"record {log_id} was withdrawn before release")
