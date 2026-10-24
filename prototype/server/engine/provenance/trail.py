"""Claims, cards and declared state rebuilt from events (provenance.md section 3). Pure."""
from __future__ import annotations

from dataclasses import dataclass, field

from .sources import coach_answer_from_runs


@dataclass
class Card:
    card_id: str
    text: str = ""
    origin_runs: list = field(default_factory=list)
    via: str = "typed"
    via_ref: str | None = None
    deleted: bool = False
    anchors: set = field(default_factory=set)  # (source_id, block_id)


@dataclass
class Claim:
    claim_id: str
    text: str = ""
    card_ids: list = field(default_factory=list)
    parent_claim_id: str | None = None
    kind: str = "student"  # student | declared
    import_id: str | None = None
    edit_seqs: list = field(default_factory=list)


def uncovered_chars(text: str, origin_runs) -> int:
    """Chars of text not covered by a typed run count as pasted (fail closed)."""
    typed = coach_answer_from_runs(text, list(origin_runs or [])).typed_ranges
    return len(text) - sum(b - a for a, b in typed)


def card_paste_chars(card: Card) -> int:
    return uncovered_chars(card.text, card.origin_runs)


def card_pasted(card: Card, pct: int) -> bool:
    n = len(card.text)
    return n > 0 and card_paste_chars(card) * 100 >= pct * n


def card_ends(card: Card | None, pct: int) -> tuple[tuple[str, ...], str | None]:
    if card is None or card.deleted:
        return ((), "card_not_found")
    if card_pasted(card, pct):
        return ((), "card_pasted")
    ends = set()
    if card.anchors:
        ends.add("block")
    if card.via == "coach_answer":
        ends.add("coach")
    if card.via == "import":
        ends.add("import")
    if not ends:
        return ((), "card_not_anchored")
    return (tuple(sorted(ends)), None)


@dataclass(frozen=True)
class Trail:
    cards: dict
    claims: dict

    def card(self, card_id) -> Card | None:
        return self.cards.get(card_id)

    def claim(self, claim_id) -> Claim | None:
        return self.claims.get(claim_id)

    def card_ends(self, card_id, pct):
        return card_ends(self.cards.get(card_id), pct)

    def claim_ids(self) -> list:
        return sorted(self.claims)

    def card_ids(self) -> list:
        return sorted(self.cards)

    def claim_reanchored(self, claim: Claim, pct: int) -> bool:
        if claim.kind != "declared":
            return False
        return any("block" in self.card_ends(cid, pct)[0] for cid in claim.card_ids)


def claim_reanchored(claim: Claim, trail: Trail, pct: int) -> bool:
    return trail.claim_reanchored(claim, pct)


def build_trail(events) -> Trail:
    cards: dict = {}
    claims: dict = {}
    for e in sorted(events, key=lambda e: e["seq"]):
        t, p = e["type"], e.get("payload") or {}
        if t in ("card.create", "card.edit"):
            known = p["card_id"] in cards
            c = cards.setdefault(p["card_id"], Card(p["card_id"]))
            c.text = p.get("text") or ""
            c.origin_runs = list(p.get("origin_runs") or [])
            if t == "card.create" or not known:
                c.via = p.get("via") or "typed"
                c.via_ref = p.get("via_ref")
                c.deleted = False
            else:  # an edit keeps what it does not state, and never revives a deleted card
                if p.get("via"):
                    c.via = p["via"]
                if "via_ref" in p:
                    c.via_ref = p["via_ref"]
        elif t == "card.delete":
            if p.get("card_id") in cards:
                cards[p["card_id"]].deleted = True
        elif t == "card.anchor":
            if p.get("card_id") in cards:
                cards[p["card_id"]].anchors.add((p.get("source_id"), p.get("block_id")))
        elif t in ("claim.create", "claim.edit"):
            c = claims.setdefault(p["claim_id"], Claim(p["claim_id"]))
            c.text = p.get("text") or ""
            c.card_ids = list(p.get("card_ids") or [])
            c.parent_claim_id = p.get("parent_claim_id")
            if t == "claim.edit":
                c.edit_seqs.append(e["seq"])
        elif t == "claim.extracted":
            if p["claim_id"] not in claims:
                claims[p["claim_id"]] = Claim(p["claim_id"], text=p.get("text") or "",
                                              kind="declared", import_id=p.get("import_id"))
    return Trail(cards, claims)
