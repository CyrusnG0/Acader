"""verify(log, seal): is this record unchanged since the seal? (event-log.md §6, spike S5)

Checks, in order:
1. The chain: genesis prev_hash, gap-free seq from 0, each prev_hash links to the previous hash,
   every stored hash recomputes, one log_id, schema 1.
2. The seal: some event has this hash, and it is a `submit`.
3. After the seal: only whitelisted types, except inside a resubmission window
   (`resubmit.open` up to the next `submit`).
4. Optional, when given: stored AI outputs (artifacts) hash to what they claim and to the
   `output_hash` of the events that cite them; the receipt hashes to its `receipt.issued` event,
   names this seal, and every `event_ids` entry exists at or before `seal_seq` (or, for an element
   marked `post_seal`, is a `note.add` / `link.add` after it). `artifact_ids` must resolve.

Spike conventions (proposed in the S5 note, not yet decided): an event id is its `seq`;
an artifact is `{"body": str, "hash": sha256_hex(body)}`; `receipt_hash` is the sha256 of the
receipt's canonical JSON.
"""
from dataclasses import dataclass, field

from .canonical import CanonicalError, canonical_json, sha256_hex
from .chain import POST_SEAL_WHITELIST, SCHEMA, event_hash, genesis_prev_hash

POST_SEAL_NOTE_TYPES = frozenset({"note.add", "link.add"})


@dataclass
class VerifyResult:
    ok: bool
    problems: list[str] = field(default_factory=list)
    seal_seq: int | None = None


def _check_chain(events: list[dict], problems: list[str]) -> None:
    if not events:
        problems.append("log is empty")
        return
    log_id = events[0].get("log_id")
    prev = genesis_prev_hash(log_id)
    for i, e in enumerate(events):
        where = f"position {i} (seq {e.get('seq')}, {e.get('type')})"
        if e.get("log_id") != log_id:
            problems.append(f"{where}: log_id differs from the first event")
        if e.get("schema") != SCHEMA:
            problems.append(f"{where}: schema is not {SCHEMA}")
        if e.get("seq") != i:
            problems.append(f"{where}: expected seq {i} (gap, deletion or reordering)")
        if e.get("prev_hash") != prev:
            problems.append(f"{where}: prev_hash does not link to the previous event")
        try:
            recomputed = event_hash(e)
        except (CanonicalError, KeyError, TypeError) as exc:
            problems.append(f"{where}: cannot hash ({exc})")
            recomputed = None
        if recomputed is not None and recomputed != e.get("hash"):
            problems.append(f"{where}: stored hash does not match its content (edited)")
        prev = e.get("hash")


def _find_seal(events: list[dict], seal: str, problems: list[str]) -> int | None:
    for i, e in enumerate(events):
        if e.get("hash") == seal:
            if e.get("type") != "submit":
                problems.append(f"seal names a {e.get('type')!r} event, not a submit")
                return None
            return i
    problems.append("seal not found in the log")
    return None


def _check_after_seal(events: list[dict], seal_index: int, problems: list[str]) -> None:
    sealed = True
    for e in events[seal_index + 1:]:
        t = e.get("type")
        if sealed:
            if t not in POST_SEAL_WHITELIST:
                problems.append(f"seq {e.get('seq')}: {t!r} appended after the seal")
            elif t == "resubmit.open":
                sealed = False
        elif t == "submit":
            sealed = True


def _artifact_ok(aid: str, artifacts: dict, problems: list[str]) -> dict | None:
    a = artifacts.get(aid)
    if a is None:
        problems.append(f"artifact {aid} is not stored")
        return None
    if sha256_hex(a.get("body", "").encode("utf-8")) != a.get("hash"):
        problems.append(f"artifact {aid}: body does not match its hash")
        return None
    return a


def _check_artifacts(events: list[dict], artifacts: dict, problems: list[str]) -> None:
    for e in events:
        p = e.get("payload") or {}
        aid = p.get("artifact_id")
        if aid is None or "output_hash" not in p:
            continue
        a = _artifact_ok(aid, artifacts, problems)
        if a is not None and a["hash"] != p["output_hash"]:
            problems.append(f"seq {e.get('seq')}: output_hash differs from artifact {aid}")


def _walk(node, out: list[dict]) -> None:
    if isinstance(node, dict):
        if "event_ids" in node or "artifact_ids" in node:
            out.append(node)
        for v in node.values():
            _walk(v, out)
    elif isinstance(node, list):
        for v in node:
            _walk(v, out)


def _check_receipt(events: list[dict], seal: str, seal_index: int, receipt: dict,
                   artifacts: dict | None, problems: list[str]) -> None:
    seal_seq = events[seal_index]["seq"]
    if receipt.get("seal_hash") != seal:
        problems.append("receipt names a different seal")
    if receipt.get("seal_seq") != seal_seq:
        problems.append("receipt seal_seq differs from the seal event")
    try:
        rhash = sha256_hex(canonical_json(receipt))
    except CanonicalError as exc:
        problems.append(f"receipt cannot be hashed ({exc})")
        rhash = None
    issued = [e for e in events[seal_index + 1:]
              if e.get("type") == "receipt.issued"
              and e["payload"].get("receipt_id") == receipt.get("receipt_id")
              and e["payload"].get("version") == receipt.get("version")]
    if not issued:
        problems.append("no receipt.issued event for this receipt after the seal")
    elif rhash is not None and issued[-1]["payload"].get("receipt_hash") != rhash:
        problems.append("receipt does not match receipt_hash in its receipt.issued event")
    elif issued[-1]["payload"].get("seal_seq") != seal_seq:
        problems.append("receipt.issued names a different seal_seq")

    by_seq = {e.get("seq"): e for e in events}
    elements: list[dict] = []
    _walk(receipt, elements)
    for el in elements:
        for eid in el.get("event_ids", []):
            e = by_seq.get(eid)
            if e is None:
                problems.append(f"receipt cites event {eid}, which is not in the log")
            elif el.get("post_seal"):
                if eid <= seal_seq or e.get("type") not in POST_SEAL_NOTE_TYPES:
                    problems.append(f"receipt post-seal line cites event {eid}, not a later note")
            elif eid > seal_seq:
                problems.append(f"receipt cites event {eid}, after the seal")
        for aid in el.get("artifact_ids", []):
            if artifacts is None:
                problems.append(f"receipt cites artifact {aid} but no artifacts were given")
            else:
                _artifact_ok(aid, artifacts, problems)


def verify(events: list[dict], seal: str, *, receipt: dict | None = None,
           artifacts: dict | None = None) -> VerifyResult:
    problems: list[str] = []
    _check_chain(events, problems)
    seal_index = _find_seal(events, seal, problems) if events else None
    if seal_index is not None:
        _check_after_seal(events, seal_index, problems)
    if artifacts is not None:
        _check_artifacts(events, artifacts, problems)
    if receipt is not None and seal_index is not None:
        _check_receipt(events, seal, seal_index, receipt, artifacts, problems)
    return VerifyResult(ok=not problems, problems=problems,
                        seal_seq=events[seal_index]["seq"] if seal_index is not None else None)
