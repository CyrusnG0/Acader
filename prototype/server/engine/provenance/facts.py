"""Receipt facts, L1 only (provenance.md section 7). Pure. No construction-order measures, no
judgement of Coach answers, no timing of any kind (D-046)."""
from __future__ import annotations

from collections.abc import Mapping

from .bands import walk_textblocks
from .trail import Trail, claim_reanchored, card_paste_chars, uncovered_chars

READ_KINDS = ("abstract", "method", "results", "table", "limitation", "discussion")
OUTCOMES = ("answered", "declined", "disagreed", "revised")
READING_TYPES = ("source.add", "source.open", "source.view_span", "aid.pin_opened", "card.anchor")


def _kind(block_kinds: Mapping, block_id) -> str:
    k = block_kinds.get(block_id)
    return k if k in READ_KINDS else "other"


def _by_kind(blocks, block_kinds) -> dict:
    out: dict = {}
    for b in sorted(blocks, key=lambda x: str(x)):
        k = _kind(block_kinds, b)
        out[k] = out.get(k, 0) + 1
    return dict(sorted(out.items()))


def _reading(evs, trail: Trail, block_kinds) -> list:
    src: dict = {}
    for e in evs:
        t, p = e["type"], e.get("payload") or {}
        if t not in READING_TYPES:
            continue
        sid = p.get("source_id")
        if t == "card.anchor" and sid is None:
            continue
        s = src.setdefault(sid, {"opened": set(), "event_ids": []})
        s["event_ids"].append(e["seq"])
        if t == "source.view_span":
            s["opened"].update(p.get("block_ids") or [])
        elif t == "aid.pin_opened" and p.get("block_id") is not None:
            s["opened"].add(p["block_id"])
    anchored: dict = {}
    for c in trail.cards.values():
        if c.deleted:
            continue
        for (sid, bid) in c.anchors:
            anchored.setdefault(sid, set()).add(bid)
    out = []
    for sid in sorted(src, key=str):
        out.append({"source_id": sid, "opened": _by_kind(src[sid]["opened"], block_kinds),
                    "anchored": _by_kind(anchored.get(sid, ()), block_kinds),
                    "event_ids": sorted(set(src[sid]["event_ids"]))})
    return out


def _moments(evs) -> list:
    out = []
    pins: list = []  # (seq, source_id)
    anchors: list = []  # (seq, card_id, source_id)
    for e in evs:
        t, p, seq = e["type"], e.get("payload") or {}, e["seq"]
        if t == "aid.pin_opened" and p.get("pin_kind") == "limitation":
            pins.append((seq, p.get("source_id")))
        elif t == "card.anchor":
            anchors.append((seq, p.get("card_id"), p.get("source_id")))
        elif t == "claim.edit":
            cards = set(p.get("card_ids") or [])
            ok = {}
            for (aseq, cid, asrc) in anchors:
                if cid in cards:
                    for (pseq, psrc) in pins:
                        if psrc == asrc:
                            ok[asrc] = max(ok.get(asrc, -1), pseq)
            if ok:
                s = sorted(ok, key=str)[0]
                out.append({"kind": "claim_edit_after_limitation", "seq": seq, "ts": e.get("ts"),
                            "claim_id": p.get("claim_id"), "source_id": s, "pin_seq": ok[s]})
        elif t == "card.set_aside":
            tag = p.get("reason_tag")
            if isinstance(tag, str) and tag.strip():
                out.append({"kind": "set_aside", "seq": seq, "ts": e.get("ts"),
                            "source_id": p.get("source_id"), "reason_tag": tag})
        elif t == "coach.outcome":
            if p.get("outcome") == "disagreed" and str(p.get("answer_text") or "").strip():
                out.append({"kind": "coach_disagreed", "seq": seq, "ts": e.get("ts"),
                            "q_id": p.get("q_id")})
            elif p.get("outcome") == "revised":
                out.append({"kind": "coach_revised", "seq": seq, "ts": e.get("ts"),
                            "q_id": p.get("q_id")})
    return sorted(out, key=lambda m: m["seq"])


def _latest_outcomes(evs) -> dict:
    latest: dict = {}
    for e in evs:
        p = e.get("payload") or {}
        if e["type"] == "coach.outcome" and p.get("outcome") in OUTCOMES:
            latest[p.get("q_id")] = e
    return latest


def _coach(evs) -> dict:
    latest = _latest_outcomes(evs)
    by_case = {"B": 0, "C": 0}
    by_pillar = {k: 0 for k in ("communication", "logic", "reading", "writing")}
    by_outcome = {k: 0 for k in ("answered", "declined", "disagreed", "no_outcome", "revised")}
    questions, ids = [], []
    asked = 0
    for e in evs:
        if e["type"] != "coach.ask":
            continue
        p = e.get("payload") or {}
        asked += 1
        ids.append(e["seq"])
        if p.get("case") in by_case:
            by_case[p["case"]] += 1
        if p.get("pillar") in by_pillar:
            by_pillar[p["pillar"]] += 1
        o = latest.get(p.get("q_id"))
        outcome = o["payload"]["outcome"] if o else "no_outcome"
        by_outcome[outcome] += 1
        if o:
            ids.append(o["seq"])
        questions.append({"q_id": p.get("q_id"), "seq": e["seq"], "case": p.get("case"),
                          "pillar": p.get("pillar"), "outcome": outcome,
                          "outcome_seq": o["seq"] if o else None})
    return {"asked": asked, "by_case": by_case, "by_pillar": by_pillar, "by_outcome": by_outcome,
            "questions": questions, "event_ids": sorted(set(ids))}


def _pastes(evs, doc_chars: dict, trail: Trail) -> dict:
    items = []
    for e in evs:
        p = e.get("payload") or {}
        if e["type"] == "editor.paste" and p.get("kind") == "external":
            size = int(p.get("size_chars") or 0)
            surv = doc_chars.get(p.get("paste_id"), 0)
            items.append({"paste_id": p.get("paste_id"), "seq": e["seq"], "size_chars": size,
                          "surviving_chars": surv})
    live = [c for c in trail.cards.values() if not c.deleted]
    card_chars = [card_paste_chars(c) for c in live]
    ans_chars = []
    for e in _latest_outcomes(evs).values():
        p = e["payload"]
        txt = p.get("answer_text")
        if isinstance(txt, str) and txt:
            ans_chars.append(uncovered_chars(txt, p.get("origin_runs") or []))
    return {"editor": {"count": len(items), "chars": sum(i["size_chars"] for i in items),
                       "surviving_chars": sum(i["surviving_chars"] for i in items),
                       "items": items, "event_ids": [i["seq"] for i in items]},
            "cards": {"cards_with_paste": sum(1 for c in card_chars if c > 0),
                      "chars": sum(card_chars)},
            "coach_answers": {"answers_with_paste": sum(1 for c in ans_chars if c > 0),
                              "chars": sum(ans_chars)},
            "final_paste_ext_chars": sum(doc_chars.values())}


def _paste_survival(doc) -> dict:
    out: dict = {}
    for b in walk_textblocks(doc):
        for k, r in zip(b.kinds, b.refs):
            if k == "paste_ext":
                out[r] = out.get(r, 0) + 1
    return out


def compute_facts(events, doc, trail: Trail, *, block_kinds: Mapping | None = None,
                  paste_ext_pct: int = 50) -> dict:
    block_kinds = block_kinds or {}
    evs = sorted(events, key=lambda e: e["seq"])
    survival = _paste_survival(doc)
    repl_ids, repl = [], 0
    imports = []
    for e in evs:
        p = e.get("payload") or {}
        if e["type"] == "editor.batch":
            n = (p.get("input_kind") or {}).get("replacement", 0)
            if isinstance(n, int) and not isinstance(n, bool) and n > 0:
                repl += n
                repl_ids.append(e["seq"])
        elif e["type"] == "import.declared":
            tool = p.get("tool_name")
            tool = tool if isinstance(tool, str) and tool else "unknown"
            imports.append({"import_id": p.get("import_id"), "tool_name": tool,
                            "size_chars": int(p.get("size_chars") or 0), "seq": e["seq"]})
    by_tool: dict = {}
    for i in imports:
        t = by_tool.setdefault(i["tool_name"], {"count": 0, "size_chars": 0})
        t["count"] += 1
        t["size_chars"] += i["size_chars"]
    declared = [c for c in trail.claims.values() if c.kind == "declared"]
    unanchored = [c for c in trail.claims.values() if c.kind == "student"
                  and not any((trail.card(i) is not None and not trail.card(i).deleted)
                              for i in c.card_ids)]
    claim_ev = sorted({e["seq"] for e in evs if e["type"] in ("claim.create", "claim.edit")
                       and (e.get("payload") or {}).get("claim_id") in {c.claim_id for c in unanchored}})
    pastes = _pastes(evs, survival, trail)
    return {
        "reading": _reading(evs, trail, block_kinds),
        "moments": _moments(evs),
        "coach": _coach(evs),
        "pastes": pastes,
        "replacement_edits": {"count": repl, "lower_bound": True, "event_ids": repl_ids},
        "declared": {"imports": imports,
                     "by_tool": dict(sorted(by_tool.items(), key=lambda kv: str(kv[0]))),
                     "declared_claims": len(declared),
                     "declared_claims_anchored": sum(
                         1 for c in declared if claim_reanchored(c, trail, paste_ext_pct)),
                     "event_ids": [i["seq"] for i in imports]},
        "unanchored_claims": {"count": len(unanchored),
                              "claim_ids": sorted(c.claim_id for c in unanchored),
                              "event_ids": claim_ev},
    }
