"""Shared pieces for the S2 spike: the block shape (reading-aid.md §3), the
heading -> kind rule, the scan rule and the scoring against gold.json.

Every parser adapter returns the same ParseResult so that the comparison
measures the parser, not three different kind classifiers.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

KINDS = {"abstract", "introduction", "method", "results", "table", "figure_caption",
         "discussion", "limitation", "conclusion", "reference", "other"}

# Order matters: first match wins. A heading that matches nothing inherits the
# current kind (it is taken to be a subsection).
KIND_RULES = [
    ("reference", r"^(references|bibliography|works cited|literature cited)$"),
    ("abstract", r"^abstract$"),
    ("limitation", r"limitation|threats to validity"),
    ("other", r"appendix|acknowledg|supporting information|author contributions|funding|"
              r"competing interests|data availability|^contents$|^list of (figures|tables)$"),
    ("introduction", r"^(introduction|background)$"),
    ("results", r"^results|findings"),
    ("discussion", r"discussion"),
    ("conclusion", r"conclu"),
    ("method", r"method|materials|design|^data\b|dataset|empirical strategy|identification|experimental setup"),
]
TABLE_CAPTION = re.compile(r"^\s*(table|tab\.)\s*[A-Z]?\.?\d", re.I)
FIGURE_CAPTION = re.compile(r"^\s*(fig\.?|figure)\s*[A-Z]?\.?\d", re.I)
NUMBERING = re.compile(r"^(\d+(\.\d+)*\.?|[IVX]+\.|[A-Z](\.\d+)*\.?)\s+")

# A page "has text" when its text layer holds at least this many characters.
SCAN_MIN_CHARS_PER_PAGE = 50


def norm_heading(text: str) -> str:
    t = " ".join(text.split())
    t = NUMBERING.sub("", t)
    return t.strip(" .:").lower()


def heading_kind(text: str) -> str | None:
    h = norm_heading(text)
    for kind, pattern in KIND_RULES:
        if re.search(pattern, h):
            return kind
    return None


def collapse(text: str) -> str:
    return " ".join(text.split())


@dataclass
class Block:
    block_id: str
    page: int | None
    bbox: tuple[float, float, float, float] | None  # x0, y0, x1, y1, top-left origin, PDF points
    section: str
    kind: str
    text: str


@dataclass
class ParseResult:
    parser: str
    doc: str
    pages: int
    seconds: float
    status: str  # ok | scan | failed
    blocks: list[Block] = field(default_factory=list)
    headings: list[str] = field(default_factory=list)
    tables: int = 0  # table bodies recognised by the parser's table finder
    error: str | None = None


class BlockBuilder:
    """Walks items in reading order and assigns section and kind by rule."""

    def __init__(self, doc_id: str):
        self.doc_id = doc_id
        self.blocks: list[Block] = []
        self.headings: list[str] = []
        self.section = ""
        self.kind = "other"
        self.tables = 0

    def table(self, text: str, page, bbox) -> None:
        """A table body found by the parser's table finder."""
        self.tables += 1
        self.add(text or "[table]", page, bbox, kind="table")

    def heading(self, text: str) -> None:
        text = collapse(text)
        if not text:
            return
        self.headings.append(text)
        self.section = text
        k = heading_kind(text)
        if k is not None:
            self.kind = k
        elif self.kind == "reference":
            self.kind = "other"  # an unlabelled heading after References is back matter (appendix)

    def add(self, text: str, page, bbox, kind: str | None = None) -> None:
        text = collapse(text)
        if not text:
            return
        if kind is None:
            if TABLE_CAPTION.match(text) and len(text) < 600:
                kind = "table"
            elif FIGURE_CAPTION.match(text) and len(text) < 600:
                kind = "figure_caption"
            else:
                kind = self.kind
        assert kind in KINDS, kind
        bid = f"{self.doc_id}-b{len(self.blocks):04d}"
        self.blocks.append(Block(bid, page, tuple(round(v, 1) for v in bbox) if bbox else None,
                                 self.section, kind, text))


def status_from_blocks(blocks: list[Block], pages: int) -> str:
    chars = sum(len(b.text) for b in blocks)
    return "scan" if chars < SCAN_MIN_CHARS_PER_PAGE * max(pages, 1) else "ok"


def score(res: ParseResult, gold: dict) -> dict:
    out = {"parser": res.parser, "doc": res.doc, "pages": res.pages,
           "seconds": round(res.seconds, 1), "status": res.status,
           "blocks": len(res.blocks), "error": res.error}
    if res.blocks:
        out["page_bbox_pct"] = round(100 * sum(1 for b in res.blocks if b.page and b.bbox) / len(res.blocks))
    if "expect_status" in gold:
        out["scan_ok"] = res.status == gold["expect_status"]
        return out
    found = [norm_heading(h) for h in res.headings]
    hits = 0
    for g in gold["headings"]:
        gn = norm_heading(g)
        if any(f == gn or (len(f) > 8 and (gn.startswith(f) or f.startswith(gn))) for f in found):
            hits += 1
    out["headings"] = f"{hits}/{len(gold['headings'])}"
    out["spurious_headings"] = max(0, len(found) - hits)
    kinds = {b.kind for b in res.blocks}
    out["kinds"] = f"{sum(k in kinds for k in gold['kinds'])}/{len(gold['kinds'])}"
    out["kinds_missing"] = [k for k in gold["kinds"] if k not in kinds]
    out["tables"] = f"{res.tables}/{gold['tables']}"
    out["references"] = f"{sum(1 for b in res.blocks if b.kind == 'reference')}/~{gold['references']}"
    lim = gold["limitation"]
    phrase = lim["phrase"].lower()
    hit = [b for b in res.blocks if phrase in b.text.lower()]
    out["limitation"] = (f"{hit[0].kind} p{hit[0].page}" if hit else "not found")
    out["limitation_ok"] = bool(hit) and hit[0].kind in lim["ok_kinds"]
    out["probes"] = f"{sum(any(p.lower() in b.text.lower() for b in res.blocks) for p in gold['probes'])}/{len(gold['probes'])}"
    return out
