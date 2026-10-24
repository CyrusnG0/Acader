"""Sentence mix, chains, bands, claim units and proportions (provenance.md sections 3-6).
Pure; integers only. The config is passed in (see l1.L1Config)."""
from __future__ import annotations

import re
from dataclasses import dataclass

from prosemirror.model import Node

from engine.replay import load_schema

from .sentences import split_sentences
from .trail import Trail, claim_reanchored

BAND_ORDER = ("declared", "traced_source", "traced_coach", "student_linked", "untraced")
MIX_KEYS = ("coach", "helper", "import", "paste_ext", "quote", "typed", "unconfirmed", "unmarked")
CHECKED = ("quote", "coach", "import", "helper")
NOTE_TEXT = {"pasted_linked_not_checked": "pasted; linked by the student, not checked",
             "label_not_confirmed": "this label couldn't be confirmed against its source"}
_WORD = re.compile(r"\S+")


@dataclass(frozen=True)
class L3bResult:
    sentence_id: str
    claim_id: str
    confirmed: bool
    added: int = 0


# ---------------------------------------------------------------- walking the document
@dataclass
class Textblock:
    id: str
    node: str
    start: int  # doc position of the first content slot
    end: int
    text: str
    pos: list  # doc position of each char
    kinds: list  # raw origin kind of each char ("unmarked" when none)
    refs: list
    links: list


def _origin(node: Node):
    for m in node.marks:
        if m.type.name == "origin":
            return m.attrs["kind"], m.attrs.get("ref")
    return "unmarked", None


def walk_textblocks(doc) -> list:
    if not isinstance(doc, Node):
        doc = Node.from_json(load_schema(), doc)
    out: list = []

    def visit(node: Node, pos: int, parent, index) -> bool:
        if not node.is_textblock:
            return True
        start = pos + 1
        chars: list = []
        p_list: list = []
        kinds: list = []
        refs: list = []
        cur = start
        for child in node.content.content:
            kind, ref = _origin(child)
            if child.is_text:
                q = cur
                for ch in child.text:
                    chars.append(ch)
                    p_list.append(q)
                    kinds.append(kind)
                    refs.append(ref)
                    q += 2 if ord(ch) > 0xFFFF else 1
            else:
                chars.append("\n")
                p_list.append(cur)
                kinds.append(kind)
                refs.append(ref)
            cur += child.node_size
        links = []
        if node.type.name == "paragraph":
            links = [dict(l) for l in (node.attrs.get("links") or [])]
        out.append(Textblock(f"p{len(out) + 1}", node.type.name, start, cur, "".join(chars),
                             p_list, kinds, refs, links))
        return False

    doc.descendants(visit)
    return out


def norm_runs(runs) -> list:
    out = []
    for r in runs or ():
        d = r.to_json() if hasattr(r, "to_json") else r
        out.append({"from": d["from"], "to": d["to"], "kind": d["kind"], "ref": d.get("ref"),
                    "confirmed": bool(d["confirmed"]), "reason": d.get("reason")})
    return out


def _confirm_map(runs: list) -> dict:
    m: dict = {}
    for r in runs:
        for p in range(r["from"], r["to"]):
            m[p] = m.get(p, True) and r["confirmed"]
    return m


def effective_kind(kind: str, pos: int, cmap: dict) -> str:
    if kind in CHECKED:
        return kind if cmap.get(pos, False) else "unconfirmed"
    return kind  # typed | paste_ext | unmarked


# ---------------------------------------------------------------- chains
def _chain(link: dict, trail: Trail, cfg, card_cache: dict) -> tuple[dict, bool]:
    claim = trail.claim(link["claim_id"])
    pct = cfg.paste_ext_pct
    cards = []
    ends: set = set()
    for cid in (claim.card_ids if claim else []):
        if cid not in card_cache:
            e, b = trail.card_ends(cid, pct)
            card_cache[cid] = {"card_id": cid, "ends": list(e), "break": b}
        c = card_cache[cid]
        cards.append({"card_id": c["card_id"], "ends": list(c["ends"]), "break": c["break"]})
        ends.update(c["ends"])
    declared_unanchored = False
    if claim is None:
        kind = "missing"
    else:
        kind = claim.kind
        if kind == "declared":
            ends.add("import")
            declared_unanchored = not claim_reanchored(claim, trail, pct)
    brk = None
    if not ends:
        if claim is None:
            brk = "claim_not_found"
        elif not claim.card_ids:
            brk = "claim_has_no_cards"
        else:
            brk = cards[0]["break"]
    return ({"claim_id": link["claim_id"], "by": link.get("by"),
             "suggestion_id": link.get("suggestion_id"), "claim_kind": kind, "cards": cards,
             "ends": sorted(ends), "break": brk}, declared_unanchored)


# ---------------------------------------------------------------- the main computation
def _word_spans_all_quote(text: str, ekinds: list) -> int:
    n = 0
    for m in _WORD.finditer(text):
        if all(ekinds[i] == "quote" for i in range(m.start(), m.end())):
            n += 1
    return n


def analyse(blocks: list, runs, trail: Trail, cfg, l3b=(), map_suggestions: int = 0) -> dict:
    runs = norm_runs(runs)
    cmap = _confirm_map(runs)
    l3b_idx: dict = {}
    for r in l3b:
        l3b_idx.setdefault((r.sentence_id, r.claim_id), []).append(r)
    added_idx: dict = {}
    for r in l3b:
        added_idx[r.sentence_id] = added_idx.get(r.sentence_id, 0) + r.added
    card_cache: dict = {}

    paragraphs, sentences, queue = [], [], []
    para_sentences: dict = {}  # paragraph id -> [sentence dict]
    para_links: dict = {}
    snum = 0
    pct_paste, pct_imp, pct_unl = cfg.paste_ext_pct, cfg.declared_import_pct, cfg.unlinked_untyped_pct

    for b in blocks:
        ek = [effective_kind(k, p, cmap) for k, p in zip(b.kinds, b.pos)]
        chain_infos = [_chain(l, trail, cfg, card_cache) for l in b.links]
        sids = []
        sents = []
        for s, e in split_sentences(b.text):
            snum += 1
            sid = f"s{snum}"
            sids.append(sid)
            mix = {k: 0 for k in MIX_KEYS}
            for k in ek[s:e]:
                mix[k] += 1
            n = e - s
            frm = b.pos[s]
            to = b.pos[e - 1] + (2 if ord(b.text[e - 1]) > 0xFFFF else 1)
            imp, quo, coa = mix["import"], mix["quote"], mix["coach"]
            pas, unc = mix["paste_ext"], mix["unconfirmed"]
            clean = pas + unc == 0
            mostly_pasted = (pas + unc) * 100 >= pct_paste * n
            added = added_idx.get(sid, 0)

            def l3b_cond(end: str) -> bool:
                for (link, (chain, _)) in zip(b.links, chain_infos):
                    if link.get("suggestion_id") is not None or end not in chain["ends"]:
                        continue
                    if any(r.confirmed for r in l3b_idx.get((sid, link["claim_id"]), ())):
                        return True
                return False

            declared_unanch = any(du for (_, du) in chain_infos)
            if imp * 100 >= pct_imp * n or declared_unanch:
                band = "declared"
            elif added == 0 and clean and (quo > 0 or l3b_cond("block")):
                band = "traced_source"
            elif added == 0 and clean and (coa > 0 or l3b_cond("coach")):
                band = "traced_coach"
            elif b.links and not mostly_pasted:
                band = "student_linked"
            else:
                band = "untraced"
            notes = set()
            if b.links and mostly_pasted and band == "untraced" and pas * 100 >= pct_paste * n:
                notes.add("pasted_linked_not_checked")
            if unc > 0:
                notes.add("label_not_confirmed")
            seen, marks = set(), []
            for r in sorted((r for r in runs if r["from"] < to and r["to"] > frm),
                            key=lambda r: (r["from"], r["to"])):
                key = (r["from"], r["to"], r["kind"], r["ref"])
                if key in seen:
                    continue
                seen.add(key)
                marks.append({"kind": r["kind"], "ref": r["ref"], "confirmed": r["confirmed"],
                              "reason": r["reason"]})
            sent = {"id": sid, "paragraph_id": b.id, "from": frm, "to": to,
                    "words": len(b.text[s:e].split()), "mix": mix, "band": band,
                    "notes": sorted(notes), "added": added,
                    "quoted_words": _word_spans_all_quote(b.text[s:e], ek[s:e]), "marks": marks,
                    "chains": [c for (c, _) in chain_infos],
                    "chain_break": None if b.links else "no_link"}
            sentences.append(sent)
            sents.append(sent)
            reasons = set()
            if not b.links and (mix["typed"] + pas) * 100 >= pct_unl * n:
                reasons.add("unlinked")
            if any(l.get("by") == "student" for l in b.links):
                reasons.add("student_link")
            if pas * 100 >= pct_paste * n:
                reasons.add("pasted")
            if reasons:
                queue.append({"sentence_id": sid, "reasons": sorted(reasons)})
        para_sentences[b.id] = sents
        para_links[b.id] = b.links
        paragraphs.append({"id": b.id, "node": b.node, "from": b.start, "to": b.end,
                           "links": [dict(l) for l in b.links], "sentence_ids": sids})

    # claim units
    units, order = [], {}
    for b in blocks:
        if b.links:
            for l in b.links:
                cid = l["claim_id"]
                if cid not in order:
                    order[cid] = {"id": cid, "unit": "claim", "sents": [], "pids": set()}
                    units.append(order[cid])
                u = order[cid]
                if b.id not in u["pids"]:
                    u["pids"].add(b.id)
                    u["sents"].extend(para_sentences[b.id])
        elif b.node == "paragraph" and para_sentences[b.id]:
            units.append({"id": b.id, "unit": "paragraph", "sents": list(para_sentences[b.id]),
                          "pids": {b.id}})
    claims_out = []
    by_claims = {k: 0 for k in BAND_ORDER}
    for u in units:
        w = {k: 0 for k in BAND_ORDER}
        for s in u["sents"]:
            w[s["band"]] += s["words"]
        if u["unit"] == "claim":
            c = trail.claim(u["id"])
            ckind = "missing" if c is None else c.kind
            decl = (c is not None and c.kind == "declared"
                    and not claim_reanchored(c, trail, pct_paste))
        else:
            ckind, decl = None, False
        band = "declared" if decl else max(BAND_ORDER, key=lambda k: (w[k], BAND_ORDER.index(k)))
        by_claims[band] += 1
        claims_out.append({"id": u["id"], "unit": u["unit"], "claim_kind": ckind, "band": band,
                           "words": sum(s["words"] for s in u["sents"]),
                           "sentence_ids": [s["id"] for s in u["sents"]]})
    by_words = {k: 0 for k in BAND_ORDER}
    for s in sentences:
        by_words[s["band"]] += s["words"]
    inferred = sum(1 for b in blocks for l in b.links if l.get("suggestion_id"))
    bands = {"total_words": sum(by_words.values()), "by_words": by_words, "by_claims": by_claims,
             "quoted_words": sum(s["quoted_words"] for s in sentences),
             "inferred_links": inferred, "map_suggestions": map_suggestions}
    return {"paragraphs": paragraphs, "sentences": sentences, "claims": claims_out,
            "bands": bands, "l3b_queue": queue}
