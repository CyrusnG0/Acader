"""Compile-time replay (design/event-log.md section 5, provenance.md section 9).

Rebuilds the document from the recorded steps and checks it against every hash the
browser sent at a checkpoint. Pure: no I/O. A mismatch never raises; it is reported.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from prosemirror.model import Node

from .replay import ReplayError, doc_hash, replay_steps

EMPTY_DOC: dict = {"type": "doc", "content": [{"type": "paragraph", "attrs": {"links": []}}]}

SnapshotLoader = Callable[[str], "dict | None"]


@dataclass(frozen=True)
class CheckpointCheck:
    seq: int
    doc_rev: int
    client_hash: str
    replayed_hash: str | None
    ok: bool
    reason: str

    def to_json(self) -> dict:
        return {"seq": self.seq, "doc_rev": self.doc_rev, "client_hash": self.client_hash,
                "replayed_hash": self.replayed_hash, "ok": self.ok, "reason": self.reason}


@dataclass(frozen=True)
class ReplayReport:
    status: str
    seal_seq: int | None
    doc_rev: int
    client_hash: str | None
    built_from: str
    doc: dict
    checkpoints: tuple[CheckpointCheck, ...]

    def to_json(self) -> dict:
        return {"status": self.status, "seal_seq": self.seal_seq, "doc_rev": self.doc_rev,
                "client_hash": self.client_hash, "built_from": self.built_from,
                "doc_hash": doc_hash(self.doc),
                "checkpoints": [c.to_json() for c in self.checkpoints]}


def step_segments(events: list[dict]) -> list[tuple[int, int, list[dict]]]:
    out = []
    for e in events:
        if e["type"] != "editor.batch":
            continue
        steps = e["payload"]["steps"]
        end = e["doc_rev"]
        out.append((end - len(steps), end, steps))
    return out


def steps_between(events: list[dict], from_rev: int, to_rev: int) -> list[dict]:
    if from_rev == to_rev:
        return []
    segs = step_segments(events)
    i = next((n for n, s in enumerate(segs) if s[0] == from_rev), None)
    if i is None:
        raise ReplayError(f"steps_gap: no batch starts at rev {from_rev}")
    out: list[dict] = []
    cur = from_rev
    while cur < to_rev:
        if i >= len(segs) or segs[i][0] != cur:
            raise ReplayError(f"steps_gap: no batch continues from rev {cur}")
        out.extend(segs[i][2])
        cur = segs[i][1]
        i += 1
    if cur != to_rev:
        raise ReplayError(f"steps_gap: rev {to_rev} is not a batch boundary")
    return out


def _checkpoints(events: list[dict]) -> list[dict]:
    return [e for e in events if e["type"] == "doc.checkpoint"]


def rebuild_at(events, doc_rev, load_snapshot, *, initial_doc=EMPTY_DOC) -> Node:
    best = None
    for e in _checkpoints(events):
        if e["payload"]["doc_rev"] <= doc_rev and (
                best is None or e["payload"]["doc_rev"] >= best["payload"]["doc_rev"]):
            best = e
    if best is None:
        start, start_rev = initial_doc, 0
    else:
        start = load_snapshot(best["payload"]["snapshot_ref"])
        if start is None:
            raise ReplayError("snapshot_missing")
        start_rev = best["payload"]["doc_rev"]
    return replay_steps(start, steps_between(events, start_rev, doc_rev))


def check_replay(events, load_snapshot, *, seal_seq=None, initial_doc=EMPTY_DOC) -> ReplayReport:
    if seal_seq is None:
        subs = [e for e in events if e["type"] == "submit"]
        seal_seq = subs[-1]["seq"] if subs else None
    sealed = seal_seq is not None
    evs = [e for e in events if e["seq"] <= seal_seq] if sealed else list(events)
    cps = _checkpoints(evs)
    if sealed:
        sub = next(e for e in evs if e["type"] == "submit" and e["seq"] == seal_seq)
        final_rev = sub["payload"]["doc_rev"]
        client_hash = sub["payload"]["doc_hash"]
    else:
        segs = step_segments(evs)
        final_rev = segs[-1][1] if segs else 0
        last = cps[-1] if cps else None
        client_hash = (last["payload"]["doc_hash"]
                       if last and last["payload"]["doc_rev"] == final_rev else None)

    checks: list[CheckpointCheck] = []
    prev_doc: dict | None = initial_doc
    prev_rev = 0
    final_doc: dict | None = None
    for cp in cps:
        p = cp["payload"]
        rev, chash = p["doc_rev"], p["doc_hash"]
        replayed_hash, reason, result = None, None, None
        if prev_doc is None:
            reason = "snapshot_missing"
        else:
            try:
                result = replay_steps(prev_doc, steps_between(evs, prev_rev, rev))
                replayed_hash = doc_hash(result)
            except ReplayError as err:
                reason = "steps_gap" if str(err).startswith("steps_gap") else "replay_error"
        own = load_snapshot(p["snapshot_ref"])
        if reason is None:
            if replayed_hash != chash:
                reason = "hash_mismatch"
            elif own is None:
                reason = "snapshot_missing"
            elif doc_hash(own) != chash:
                reason = "snapshot_mismatch"
            else:
                reason = "ok"
        checks.append(CheckpointCheck(cp["seq"], rev, chash, replayed_hash, reason == "ok", reason))
        final_doc = result.to_json() if result is not None else None
        prev_doc, prev_rev = own, rev

    trailing_ok = True
    if final_rev > prev_rev or not cps:
        base = prev_doc if cps else initial_doc
        base_rev = prev_rev if cps else 0
        try:
            if base is None:
                raise ReplayError("snapshot_missing")
            final_doc = replay_steps(base, steps_between(evs, base_rev, final_rev)).to_json()
        except ReplayError:
            trailing_ok = False

    if all(c.ok for c in checks) and trailing_ok and final_doc is not None:
        return ReplayReport("ok", seal_seq, final_rev, client_hash, "replay", final_doc,
                            tuple(checks))
    # mismatch: build from the browser's stored copy of the final checkpoint
    fallback = None
    if cps:
        pick = next((c for c in reversed(cps) if c["payload"]["doc_rev"] == final_rev), cps[-1])
        fallback = load_snapshot(pick["payload"]["snapshot_ref"])
    if fallback is None:
        raise ReplayError("nothing to build from: the final snapshot is missing")
    return ReplayReport("replay_mismatch", seal_seq, final_rev, client_hash, "browser_copy",
                        fallback, tuple(checks))
