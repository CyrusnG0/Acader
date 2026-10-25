"""Compile one receipt (receipt.md sections 2, 4, 5, 6): a pure function of the sealed log, its L1,
the stored LLM outputs and the engine stamp. Integers, strings, bools, None, lists, dicts only.

Nothing here reads the wall clock, randomness or set/dict order, so the same inputs always give
the same canonical bytes (and the same receipt_hash).
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from engine.events import canonical_json, sha256_hex

from . import copy
from .questions import (TASK, Ask, ask_question, passage_for, select_candidates)
from .summary import build_summary
from .wording import WordingFilter

RECEIPT_SCHEMA = 1
ENGINE_VERSION = "receipt/1 l1/1"
BLIND_SPOTS = ["retyped", "offline", "undeclared_outside", "understanding"]
STAMP_KEYS = ("version", "git_sha", "lock_hash", "editor_pair", "models", "prompt_hashes")

# Keys whose string values are identifiers or fixed codes, never prose (left out of the sweep).
_ID_KEYS = frozenset({"receipt_id", "log_id", "seal_hash", "id", "ts", "status", "built_from",
                      "why", "pillar", "kind", "outcome", "case", "grounding",
                      "blind_spots"})


@dataclass(frozen=True)
class ReceiptResult:
    receipt: dict
    artifacts: dict  # artifact_id -> artifact (all compile artifacts, cited or not)
    receipt_hash: str  # sha256_hex(canonical_json(receipt))

    def issued_payload(self) -> dict:
        r = self.receipt
        return {"receipt_id": r["receipt_id"], "receipt_hash": self.receipt_hash,
                "seal_seq": r["seal_seq"], "version": r["version"]}


def receipt_id_for(log_id, seal_hash, version) -> str:
    return "r_" + sha256_hex(f"{log_id}/{seal_hash}/{version}".encode())[:16]


def _is_id_key(key) -> bool:
    return isinstance(key, str) and (key in _ID_KEYS or key.endswith("_id") or key.endswith("_ids"))


def _sweep(node, wf: WordingFilter, key=None):
    if isinstance(node, dict):
        return {k: _sweep(v, wf, k) for k, v in node.items()}
    if isinstance(node, list):
        return [_sweep(v, wf, key) for v in node]
    if isinstance(node, str) and not _is_id_key(key):
        return wf.apply(node, copy.FALLBACK_TEXT)
    return node


def _latest_titles(evs) -> dict:
    out: dict = {}
    for e in evs:
        if e["type"] == "source.add":
            p = e.get("payload") or {}
            out[p.get("source_id")] = p.get("title")
    return out


def _stored_index(stored: Mapping | None) -> dict:
    idx: dict = {}
    for a in (stored or {}).values():
        try:
            if sha256_hex(a["body"].encode("utf-8")) != a["hash"]:
                continue
            idx[(a["task"], a["prompt_hash"])] = a
        except (KeyError, TypeError, AttributeError):
            continue
    return idx


def compile_receipt(*, events, l1: dict, doc, log_id: str, seal_hash: str, sources, stamp: dict,
                    ask: Ask | None, stored: Mapping | None = None,
                    version: int = 1) -> ReceiptResult:
    seal = next((e for e in events if e.get("hash") == seal_hash), None)
    if seal is None or seal["type"] != "submit":
        raise ValueError("seal_hash does not name a submit event")
    seal_seq = seal["seq"]
    evs = sorted((e for e in events if e["seq"] <= seal_seq), key=lambda e: e["seq"])
    wf = WordingFilter()
    facts, bands = l1["facts"], l1["bands"]

    # ---- questions
    cands, more, skipped = select_candidates(l1, evs, doc, seal_seq=seal_seq, sources=sources)
    index = _stored_index(stored)
    artifacts: dict = {}
    questions: list = []
    down = False
    for c in cands:
        fields, arts, down = ask_question(c, passage_for(doc, c["paragraph_id"]), ask, index,
                                          llm_down=down)
        for a in arts:
            artifacts[a["artifact_id"]] = a
        questions.append({
            "q": fields["q"] if fields else None,
            "pillar": fields["pillar"] if fields else None,
            "why": c["why"], "why_text": copy.WHY_TEXT[c["why"]],
            "paragraph_id": c["paragraph_id"], "span": dict(c["span"]),
            "grounding": fields["grounding"] if fields else [],
            "event_ids": list(c["event_ids"]),
            "artifact_ids": sorted(set(c["source_artifact_ids"]) | {a["artifact_id"] for a in arts}),
        })
    pending = any(q["q"] is None for q in questions)
    status = ("replay_mismatch" if l1["status"] == "replay_mismatch"
              else "questions_pending" if pending else "complete")

    # ---- more places to ask (D-060): no generated wording and no provider call. These are
    # grounded places the top questions did not use, in paragraph order, with the existing
    # plain reason copy. Each cites its grounding ids and event ids (unless a mapper artifact
    # is stored, nothing here needs artifact_ids).
    more_places = [{
        "paragraph_id": c["paragraph_id"], "span": dict(c["span"]),
        "why": c["why"], "why_text": copy.WHY_TEXT[c["why"]],
        "grounding": [i["id"] for i in c["grounding_items"]],
        "event_ids": list(c["event_ids"]),
    } for c in more]

    # ---- the rest
    titles = _latest_titles(evs)
    moments = []
    for m in facts["moments"]:
        d = {"kind": m["kind"], "ts": m["ts"]}
        for k in ("claim_id", "source_id", "q_id", "reason_tag"):
            if k in m:
                d[k] = m[k]
        d["event_ids"] = sorted({m["seq"]} | ({m["pin_seq"]} if m.get("pin_seq") is not None
                                               else set()))
        moments.append(d)

    fc = facts["coach"]
    coach = {"asked": fc["asked"], "by_case": fc["by_case"], "by_pillar": fc["by_pillar"],
             "by_outcome": fc["by_outcome"],
             "questions": [{"q_id": q["q_id"], "case": q["case"], "pillar": q["pillar"],
                            "outcome": q["outcome"],
                            "event_ids": [q["seq"]] + ([q["outcome_seq"]]
                                                       if q["outcome_seq"] is not None else [])}
                           for q in fc["questions"]],
             "event_ids": fc["event_ids"]}

    reading = []
    for r in facts["reading"]:
        t = titles.get(r["source_id"])
        reading.append({"source_id": r["source_id"],
                        "title": wf.apply(t, copy.FALLBACK_TITLE) if isinstance(t, str) else None,
                        "opened": r["opened"], "anchored": r["anchored"],
                        "event_ids": r["event_ids"]})

    fd = facts["declared"]
    by_tool = [{"tool_name": wf.apply(name, copy.FALLBACK_TOOL), "count": v["count"],
                "size_chars": v["size_chars"]} for name, v in sorted(fd["by_tool"].items())]
    declared = {"imports": [{"import_id": i["import_id"],
                             "tool_name": wf.apply(i["tool_name"], copy.FALLBACK_TOOL),
                             "size_chars": i["size_chars"], "event_ids": [i["seq"]]}
                            for i in fd["imports"]],
                "by_tool": by_tool, "declared_claims": fd["declared_claims"],
                "declared_claims_anchored": fd["declared_claims_anchored"],
                "event_ids": fd["event_ids"]}

    fr = facts["replacement_edits"]
    status_note = copy.REPLAY_NOTE if status == "replay_mismatch" else None
    body = {
        "receipt_id": receipt_id_for(log_id, seal_hash, version), "log_id": log_id,
        "seal_hash": seal_hash, "seal_seq": seal_seq, "version": version,
        "schema": RECEIPT_SCHEMA, "status": status, "questions_pending": pending,
        "built_from": l1["built_from"], "replay_note": status_note,
        "summary": build_summary(l1, evs, seal_seq=seal_seq, wf=wf),
        "questions": questions,
        "more_places": more_places,
        "bands": {"total_words": bands["total_words"], "by_words": bands["by_words"],
                  "by_claims": bands["by_claims"], "mechanics": bands["mechanics"],
                  "quoted_words": bands["quoted_words"], "event_ids": [seal_seq]},
        "moments": moments, "coach": coach, "reading": {"sources": reading},
        "declared": declared,
        "facts": {"pastes": facts["pastes"],
                  "replacement_edits": {"count": fr["count"], "lower_bound": True,
                                        "reported_by": copy.REPLACEMENT_REPORTED_BY,
                                        "event_ids": fr["event_ids"]},
                  "unanchored_claims": facts["unanchored_claims"]},
        "inferred_links": bands["inferred_links"], "map_suggestions": bands["map_suggestions"],
        "blind_spots": list(BLIND_SPOTS),
    }
    receipt = _sweep(body, wf)  # the final sweep, before the stamp is written
    receipt["engine"] = {**{k: stamp[k] for k in STAMP_KEYS},
                         "flags": l1["engine"]["flags"], "thresholds": l1["engine"]["thresholds"],
                         "wording_filter": {"version": 1, "replaced": wf.replaced,
                                            "skipped_no_grounding": skipped}}
    h = sha256_hex(canonical_json(receipt))  # raises on a float
    return ReceiptResult(receipt, artifacts, h)
