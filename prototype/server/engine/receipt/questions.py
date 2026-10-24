"""Questions worth asking (receipt.md section 4): candidate choice, grounding, the prompt, the
output check and the asking loop. The LLM is injected as a callable; nothing here imports app/.

Reserved `why` codes that need later layers (not built at L1):
  2 "added_proposition" (L3b), 3 "contradiction" (L3c), 4 "inconsistent_standard".
D-046: nothing here ranks by event order, timestamps or Coach outcome content.
"""
from __future__ import annotations

import json
import re
import string
from collections.abc import Callable
from pathlib import Path

from engine.events import CanonicalError, canonical_json, sha256_hex
from engine.provenance import MECHANICS, build_trail
from engine.provenance.bands import walk_textblocks

from . import copy
from .wording import is_clean

TASK = "receipt_question"
PROMPT_PATH = Path(__file__).parent / "prompts" / "receipt_question.v1.txt"
PILLARS = ("reading", "logic", "writing", "communication")
MAX_GROUNDING = 6
MAX_GROUNDING_CHARS = 400
MAX_PASSAGE_CHARS = 1500

ASKS_ORIGIN = re.compile(
    r"\bhow did you (think|come up|arrive|get|decide|find|choose to write)\b"
    r"|\bwhat made you (think|write)\b"
    r"|\bwhere did (you|this|that|it|the idea|this idea)\b.*\b(come from|get|find)\b"
    r"|\bwhere (does|do) (this|that|it|the idea|these ideas?) come from\b"
    r"|\bcome up with\b", re.IGNORECASE)
CONSTRUCTION_ORDER = re.compile(
    r"\b(which|what) (came|did you do|did you write|was written) first\b"
    r"|\bin what order\b|\bbefore or after\b|\b(card|cards|outline) (first|before)\b",
    re.IGNORECASE)
ABOUT_THE_TRACE = re.compile(
    r"\b(paste|pasted|pasting|copy|copied|copying|typed|typing|traced?|untraced|generat\w*"
    r"|chatgpt|ai|a\.i\.|declared?|outside help|own words|write this|wrote this|written by"
    r"|did you write|who wrote)\b", re.IGNORECASE)


# ---------------------------------------------------------------- candidate selection
def _titles(events) -> dict:
    out: dict = {}
    for e in events:  # events are sorted by seq: the latest source.add wins
        if e["type"] == "source.add":
            p = e.get("payload") or {}
            out[p.get("source_id")] = p.get("title")
    return out


def _skey(pair):
    return (str(pair[0]), str(pair[1]))


def _grounding(trail, sources, titles, claim_id) -> list:
    items: list = []

    def add_blocks(pairs):
        for (sid, bid) in sorted(pairs, key=_skey):
            if len(items) >= MAX_GROUNDING:
                return
            txt = sources.block_text(bid)
            if not txt:
                continue
            t = titles.get(sid)
            items.append({"kind": "block", "id": bid, "text": txt[:MAX_GROUNDING_CHARS],
                          "title": t if isinstance(t, str) and t else None})

    claim = trail.claim(claim_id) if claim_id is not None else None
    if claim is not None:
        if claim.text:
            items.append({"kind": "declared" if claim.kind == "declared" else "claim",
                          "id": claim.claim_id, "text": claim.text[:MAX_GROUNDING_CHARS],
                          "title": None})
        pairs = set()
        for cid in claim.card_ids:
            c = trail.card(cid)
            if c is not None and not c.deleted:
                pairs.update(c.anchors)
        add_blocks(pairs)
    else:
        for c in sorted((c for c in trail.claims.values() if c.kind == "student" and c.text),
                        key=lambda c: c.claim_id):
            if len(items) < MAX_GROUNDING:
                items.append({"kind": "claim", "id": c.claim_id,
                              "text": c.text[:MAX_GROUNDING_CHARS], "title": None})
        pairs = set()
        for c in trail.cards.values():
            if not c.deleted:
                pairs.update(c.anchors)
        add_blocks(pairs)
    items = items[:MAX_GROUNDING]
    return [{"label": f"g{i + 1}", **it} for i, it in enumerate(items)]


def _claim_event_ids(events, trail, claim_id) -> set:
    claim = trail.claim(claim_id)
    if claim is None:
        return set()
    cards = set(claim.card_ids)
    out = set()
    for e in events:
        t, p = e["type"], e.get("payload") or {}
        if t in ("claim.create", "claim.edit", "claim.extracted") and p.get("claim_id") == claim_id:
            out.add(e["seq"])
        elif t in ("card.create", "card.edit", "card.anchor") and p.get("card_id") in cards:
            out.add(e["seq"])
        elif (t == "import.declared" and claim.kind == "declared" and claim.import_id is not None
              and p.get("import_id") == claim.import_id):
            out.add(e["seq"])
    return out


def select_candidates(l1: dict, events: list, doc, *, seal_seq: int, sources,
                      limit: int = 3) -> tuple:
    """Return (candidates, skipped_no_grounding). Only events with seq <= seal_seq are used.

    `sources` (block_text lookup) is an added keyword: grounding needs the block texts.
    """
    evs = sorted((e for e in events if e["seq"] <= seal_seq), key=lambda e: e["seq"])
    trail = build_trail(evs)
    titles = _titles(evs)
    sents = {s["id"]: s for s in l1["sentences"]}
    body = [p for p in l1["paragraphs"] if p["node"] == "paragraph"
            and any(sents[i]["band"] != MECHANICS for i in p["sentence_ids"])]
    order = {p["id"]: n for n, p in enumerate(body)}  # 0-based document order
    by_id = {p["id"]: p for p in body}
    edge = {body[0]["id"], body[-1]["id"]} if body else set()
    dependents = {c.parent_claim_id for c in trail.claims.values() if c.parent_claim_id}

    def build(why, p, unit_id, claim_id, extra_events=(), artifacts=()):
        items = _grounding(trail, sources, titles, claim_id)
        ev = {seal_seq} | set(extra_events)
        if claim_id is not None:
            ev |= _claim_event_ids(evs, trail, claim_id)
        return {"why": why, "paragraph_id": p["id"], "paragraph_number": order[p["id"]] + 1,
                "span": {"from": p["from"], "to": p["to"]}, "unit_id": unit_id,
                "claim_id": claim_id, "grounding_items": items,
                "event_ids": sorted(x for x in ev if x <= seal_seq),
                "source_artifact_ids": list(artifacts)}

    rows = []
    for u in l1["claims"]:
        sids = set(u["sentence_ids"])
        pids = []
        for sid in u["sentence_ids"]:
            pid = sents[sid]["paragraph_id"]
            if pid in by_id and pid not in pids:
                pids.append(pid)
        if not pids:
            continue

        def band_words(pid, u=u, sids=sids):
            return sum(sents[i]["words"] for i in by_id[pid]["sentence_ids"]
                       if i in sids and sents[i]["band"] == u["band"])
        anchor = min(pids, key=lambda pid: (-band_words(pid), order[pid]))
        unit_words = sum(sents[i]["words"] for i in u["sentence_ids"]
                         if sents[i]["band"] == u["band"])
        carries = (any(pid in edge for pid in pids)
                   or (u["unit"] == "claim" and u["id"] in dependents))
        rows.append((u, by_id[anchor], unit_words, carries))
    rows.sort(key=lambda r: (-r[2], order[r[1]["id"]], r[0]["id"]))

    ordered = []
    ordered += [("untraced_claim", r) for r in rows if r[0]["band"] == "untraced" and r[3]]
    ordered += [("declared_not_anchored", r) for r in rows
                if r[0]["unit"] == "claim" and r[0]["claim_kind"] == "declared"
                and r[0]["band"] == "declared"]
    ordered += [("student_linked_claim", r) for r in rows
                if r[0]["band"] == "student_linked" and r[3]]
    cands = [build(w, r[1], r[0]["id"], r[0]["id"] if r[0]["unit"] == "claim" else None)
             for (w, r) in ordered]
    cands += _finding_candidates(l1, evs, trail, body, build)

    out, used, skipped = [], set(), 0
    for c in cands:
        if c["paragraph_id"] in used:
            continue
        if not c["grounding_items"]:
            skipped += 1  # law 2: no grounding, no question
            continue
        used.add(c["paragraph_id"])
        out.append(c)
        if len(out) >= limit:
            break
    return out, skipped


def _finding_candidates(l1, evs, trail, body, build) -> list:
    asks: dict = {}
    outcomes: dict = {}
    suggestion_para: dict = {}
    for e in evs:
        p = e.get("payload") or {}
        if e["type"] == "coach.ask":
            asks.setdefault(p.get("trigger_ref"), []).append((e["seq"], p.get("q_id")))
        elif e["type"] == "coach.outcome":
            outcomes.setdefault(p.get("q_id"), []).append(e["seq"])
        elif e["type"] == "map.suggestion":
            suggestion_para[p.get("suggestion_id")] = p.get("paragraph")
    refused = set()
    for e in evs:
        p = e.get("payload") or {}
        if e["type"] == "map.answer" and p.get("answer") == "no" \
                and p.get("suggestion_id") in suggestion_para:
            refused.add(suggestion_para[p["suggestion_id"]])
    out = []
    for e in evs:
        if e["type"] != "map.finding":
            continue
        p = e.get("payload") or {}
        fid, kind = p.get("finding_id"), p.get("kind")
        if kind not in ("unconnected_paragraph", "claim_without_source"):
            continue
        if any(q is not None and any(s > aseq for s in outcomes.get(q, ()))
               for (aseq, q) in asks.get(fid, ())):
            continue  # answered
        span = p.get("span") or {}
        frm = span.get("from")
        if isinstance(frm, bool) or not isinstance(frm, int):
            continue
        para = next((b for b in body if b["from"] <= frm < b["to"]), None)
        if para is None or para["id"] in refused:
            continue
        cid = p.get("claim_id")
        if kind == "unconnected_paragraph":
            if para["links"]:
                continue
        else:
            if cid is None or trail.claim(cid) is None:
                continue
            if any(c.get("claim_id") == cid and "block" in c.get("ends", ())
                   for s in l1["sentences"] for c in s["chains"]):
                continue
        art = [p["artifact_id"]] if p.get("artifact_id") else []
        out.append(build("map_finding_" + kind, para, fid, cid, extra_events=(e["seq"],),
                         artifacts=art))
    return out


# ---------------------------------------------------------------- prompt and validation
def prompt_file_hash() -> str:
    return sha256_hex(PROMPT_PATH.read_bytes())


def _prompt_parts() -> tuple:
    text = PROMPT_PATH.read_text(encoding="utf-8")
    _, rest = text.split("=== system ===\n", 1)
    system, user = rest.split("=== user ===\n", 1)
    return system.strip(), user


def passage_for(doc, paragraph_id: str) -> str:
    for b in walk_textblocks(doc):
        if b.id == paragraph_id:
            return b.text
    return ""


def _grounding_line(it: dict) -> str:
    if it["kind"] == "claim":
        return copy.GROUNDING_CLAIM.format(label=it["label"], text=it["text"])
    if it["kind"] == "declared":
        return copy.GROUNDING_DECLARED.format(label=it["label"], text=it["text"])
    if it.get("title"):
        return copy.GROUNDING_BLOCK.format(label=it["label"], title=it["title"], text=it["text"])
    return copy.GROUNDING_BLOCK_UNTITLED.format(label=it["label"], text=it["text"])


def build_messages(candidate: dict, passage: str, retry_reason: str | None) -> list:
    system, user_t = _prompt_parts()
    user = string.Template(user_t).substitute(
        paragraph_number=str(candidate["paragraph_number"]),
        passage=passage[:MAX_PASSAGE_CHARS],
        grounding="\n".join(_grounding_line(i) for i in candidate["grounding_items"]),
        retry_note="" if retry_reason is None else copy.RETRY_NOTE.format(reason=retry_reason))
    return [{"role": "system", "content": system}, {"role": "user", "content": user.strip()}]


def validate_output(out, labels: set) -> str | None:
    if (not isinstance(out, dict) or set(out) != {"question", "pillar", "cites"}
            or not isinstance(out["question"], str) or not isinstance(out["pillar"], str)
            or not isinstance(out["cites"], list)
            or not all(isinstance(c, str) for c in out["cites"])):
        return "shape"
    if out["pillar"] not in PILLARS:
        return "pillar"
    if not out["cites"] or any(c not in labels for c in out["cites"]):
        return "cites"
    q = out["question"].strip()
    if not q.endswith("?"):
        return "not_a_question"
    if not 5 <= len(q.split()) <= 30:
        return "length"
    if not is_clean(q):
        return "wording"
    if ASKS_ORIGIN.search(q):
        return "asks_origin"
    if CONSTRUCTION_ORDER.search(q):
        return "construction_order"
    if ABOUT_THE_TRACE.search(q):
        return "about_the_trace"
    return None


# ---------------------------------------------------------------- asking
class LLMUnavailable(Exception):
    """The LLM is down (any boundary error except a schema failure)."""


class OutputRejected(Exception):
    """The boundary got output that is not valid JSON or does not fit its schema."""


Ask = Callable[[list], dict]


def make_artifact(task: str, prompt_hash: str, body: str) -> dict:
    return {"artifact_id": "a_" + sha256_hex(f"{task}\n{prompt_hash}\n{body}".encode())[:24],
            "task": task, "prompt_hash": prompt_hash, "body": body,
            "hash": sha256_hex(body.encode())}


def prompt_hash(messages) -> str:
    return sha256_hex(canonical_json(messages))


def ask_question(candidate: dict, passage: str, ask: Ask | None, stored_index: dict, *,
                 llm_down: bool) -> tuple:
    """Up to two attempts. Returns (question_fields | None, artifacts, llm_down)."""
    labels = {i["label"]: i for i in candidate["grounding_items"]}
    artifacts: list = []
    reason = None
    for _ in range(2):
        messages = build_messages(candidate, passage, reason)
        ph = prompt_hash(messages)
        stored = stored_index.get((TASK, ph))
        if stored is not None:
            try:
                out = json.loads(stored["body"])
            except (ValueError, TypeError):
                out = None
            artifacts.append(stored)
        else:
            if ask is None or llm_down:
                return None, artifacts, True
            try:
                out = ask(messages)
            except LLMUnavailable:
                return None, artifacts, True
            except OutputRejected:
                reason = "schema"
                continue
            try:
                body = canonical_json(out).decode("utf-8")
            except CanonicalError:  # e.g. a float: not storable, so not usable
                reason = "schema"
                continue
            artifacts.append(make_artifact(TASK, ph, body))
        reason = validate_output(out, set(labels))
        if reason is None:
            ids: list = []
            for label in sorted(labels, key=lambda x: int(x[1:])):
                if label in out["cites"] and labels[label]["id"] not in ids:
                    ids.append(labels[label]["id"])
            return ({"q": out["question"].strip(), "pillar": out["pillar"], "grounding": ids},
                    artifacts, llm_down)
    return None, artifacts, llm_down
