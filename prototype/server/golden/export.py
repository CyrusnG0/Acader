"""Deterministic, stub-only review export of the real synthetic golden receipts.

The compiled receipt and its hash are preserved verbatim. Synthetic presentation
metadata and sentence evidence live in a separately named view_context; they are
not fields produced by the receipt compiler or a production student endpoint.
"""
from __future__ import annotations

import os
from pathlib import Path

from engine.events import canonical_json, sha256_hex

from .build import BuildError, build_session
from .script import list_sessions, load_script
from .view_context import build_view_context

EXPORT_SCHEMA = 1


def export_gallery() -> dict:
    """Build all existing goldens without live calls, credentials, or URL fetching."""
    if os.environ.get("ROOM_LLM") != "stub":
        raise BuildError("golden export requires ROOM_LLM=stub; live calls are not allowed")
    sessions = []
    for index, session_id in enumerate(list_sessions()):
        script = load_script(session_id)
        result = build_session(session_id)
        if result.receipt_hash != sha256_hex(canonical_json(result.receipt)):
            raise BuildError(f"receipt hash does not match compiled receipt: {session_id}")
        context = build_view_context(result, script, index)
        if context.get("synthetic") is not True:
            raise BuildError(f"view context must identify synthetic sample: {session_id}")
        header = context.get("header")
        if (not isinstance(header, dict) or not isinstance(header.get("student_name"), str)
                or not header["student_name"].strip()):
            raise BuildError(f"view context needs a synthetic student name: {session_id}")
        sessions.append({"session_id": session_id, "receipt": result.receipt,
                         "receipt_hash": result.receipt_hash, "view_context": context})
    sessions.sort(key=lambda item: (item["view_context"]["header"]["student_name"].casefold(),
                                    item["session_id"]))
    return {"schema_version": EXPORT_SCHEMA, "synthetic": True, "sessions": sessions}


def write_gallery(output: str | Path) -> Path:
    """Write only after the full export has built and passed canonical validation."""
    body = canonical_json(export_gallery()) + b"\n"
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    return path
