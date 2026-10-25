"""The hash chain: genesis, event hashes, the seal and the post-seal whitelist (event-log.md §3, §6)."""
from .canonical import canonical_json, sha256_hex

SCHEMA = 1

# After a seal, only these may append (event-log.md §6, D8).
POST_SEAL_WHITELIST = frozenset(
    {"receipt.issued", "note.add", "link.add", "resubmit.open"}
)


class SealedError(Exception):
    """Append refused: the log is sealed and the event type is not whitelisted (HTTP 409)."""


def genesis_prev_hash(log_id: str) -> str:
    return sha256_hex(("writing-room/" + log_id).encode("utf-8"))


def event_hash(event: dict) -> str:
    """hash = sha256(prev_hash || canonical_json(envelope without hash)).

    `prev_hash` is concatenated as its lowercase hex text (UTF-8), then the canonical JSON bytes.
    """
    body = {k: v for k, v in event.items() if k != "hash"}
    return sha256_hex(event["prev_hash"].encode("utf-8") + canonical_json(body))


def is_sealed(events: list[dict]) -> bool:
    """True when the latest `submit` is not followed by a `resubmit.open`."""
    sealed = False
    for e in events:
        if e["type"] == "submit":
            sealed = True
        elif e["type"] == "resubmit.open":
            sealed = False
    return sealed


def build_event(head: dict | None, log_id: str, *, type: str, actor: str, payload: dict,
                ts: str, client_seq: int | None = None, doc_rev: int | None = None,
                sealed: bool = False) -> dict:
    """Make the next event after `head` (None for the first event). Pure: no I/O."""
    if sealed and type not in POST_SEAL_WHITELIST:
        raise SealedError(f"log {log_id} is sealed; {type!r} may not append")
    event = {
        "schema": SCHEMA,
        "log_id": log_id,
        "seq": 0 if head is None else head["seq"] + 1,
        "client_seq": client_seq,
        "ts": ts,
        "actor": actor,
        "type": type,
        "payload": payload,
        "doc_rev": doc_rev,
        "prev_hash": genesis_prev_hash(log_id) if head is None else head["hash"],
    }
    event["hash"] = event_hash(event)
    return event
