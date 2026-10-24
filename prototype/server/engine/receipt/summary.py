"""The one-paragraph summary (receipt.md section 2 item 2): facts only, wording from copy.py."""
from __future__ import annotations

from engine.provenance import BAND_ORDER

from . import copy
from .wording import WordingFilter


def _join(parts: list) -> str:
    if len(parts) <= 1:
        return "".join(parts)
    if len(parts) == 2:
        return " and ".join(parts)
    return ", ".join(parts[:-1]) + ", and " + parts[-1]


def build_summary(l1: dict, events: list, *, seal_seq: int, wf: WordingFilter) -> dict:
    evs = sorted((e for e in events if e["seq"] <= seal_seq), key=lambda e: e["seq"])
    facts, bands = l1["facts"], l1["bands"]
    batches = [e for e in evs if e["type"] == "editor.batch"]
    days = len({e["ts"][:10] for e in batches})
    adds = [e for e in evs if e["type"] == "source.add"]
    n_sources = len({(e.get("payload") or {}).get("source_id") for e in adds})
    src = copy.plural(copy.SUMMARY_SOURCES, n_sources)
    sentences = [(copy.plural(copy.SUMMARY_DAYS, days) + " " + src) if days > 0
                 else "Written " + src]

    total = sum(bands["by_claims"].values())
    if total > 0:
        parts = [copy.plural(copy.SUMMARY_CLAIM_PARTS[b], bands["by_claims"][b])
                 for b in BAND_ORDER if bands["by_claims"][b] > 0]
        sentences.append(copy.plural(copy.SUMMARY_CLAIMS_LEAD, total) + ", " + _join(parts))
    empty = total == 0 and bands["total_words"] == 0
    if empty:
        sentences.append(copy.SUMMARY_EMPTY)
    else:
        pastes = facts["pastes"]["editor"]["count"]
        if pastes > 0:
            sentences.append(copy.plural(copy.SUMMARY_PASTES, pastes))
        imports = facts["declared"]["imports"]
        if imports:
            tools: list = []
            for name in sorted({i["tool_name"] for i in imports}):
                t = wf.apply(name, copy.FALLBACK_TOOL)
                if t not in tools:
                    tools.append(t)
            sentences.append(copy.SUMMARY_DECLARED.format(tools=", ".join(tools)))
        coach = facts["coach"]
        if coach["asked"] > 0:
            lead = copy.plural(copy.SUMMARY_COACH_LEAD, coach["asked"])
            outs = [copy.SUMMARY_COACH_PARTS[k].format(n=coach["by_outcome"][k])
                    for k in ("answered", "revised", "disagreed", "declined")
                    if coach["by_outcome"][k] > 0]
            sentences.append(lead + (": " + ", ".join(outs) if outs else ""))
        if bands["mechanics"] > 0:
            sentences.append(copy.plural(copy.SUMMARY_MECHANICS, bands["mechanics"]))

    text = wf.apply(". ".join(sentences) + ".", copy.FALLBACK_SUMMARY)
    ids = {seal_seq} | {e["seq"] for e in adds} | {e["seq"] for e in batches}
    ids |= set(facts["pastes"]["editor"]["event_ids"]) | set(facts["declared"]["event_ids"])
    ids |= set(facts["coach"]["event_ids"])
    return {"text": text, "event_ids": sorted(ids)}
