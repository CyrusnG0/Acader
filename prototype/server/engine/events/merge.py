"""Pure helpers for the 5-minute editor.batch merge (event-log.md §5). No I/O."""
from datetime import datetime, timezone

WINDOW_MINUTES = 5
INPUT_KINDS = ("keyboard", "ime", "dictation", "replacement")
_FMT = "%Y-%m-%dT%H:%M:%SZ"


def _check_aware(dt: datetime) -> None:
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        raise ValueError("datetime must be timezone-aware")


def floor_window(dt: datetime) -> datetime:
    """Round a tz-aware time DOWN to the start of its 5-minute window, in UTC."""
    _check_aware(dt)
    u = dt.astimezone(timezone.utc)
    return u.replace(minute=u.minute - u.minute % WINDOW_MINUTES, second=0, microsecond=0)


def ts_window(dt: datetime) -> str:
    return floor_window(dt).strftime(_FMT)


def ts_seconds(dt: datetime) -> str:
    _check_aware(dt)
    return dt.astimezone(timezone.utc).replace(microsecond=0).strftime(_FMT)


def merge_batches(batches: list[dict]) -> dict:
    """Concatenate steps in order and sum input kinds. Nothing else: no counts, no times."""
    steps: list = []
    kinds = {k: 0 for k in INPUT_KINDS}
    for b in batches:
        steps.extend(b.get("steps", []))
        for k, v in (b.get("input_kind") or {}).items():
            if k in kinds:
                kinds[k] += v
    return {"steps": steps, "input_kind": kinds}


def count_words(doc: dict) -> int:
    """Whitespace-separated tokens in a ProseMirror doc; every non-text node is a boundary."""
    parts: list[str] = []

    def walk(node):
        if not isinstance(node, dict):
            return
        if node.get("type") == "text":
            parts.append(str(node.get("text", "")))
            return
        parts.append(" ")
        for child in node.get("content") or []:
            walk(child)
        parts.append(" ")

    walk(doc)
    return len("".join(parts).split())
