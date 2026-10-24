"""Check that each origin mark in the final document points at text that really exists in its
source (provenance.md section 4.1). A run that fails is left unconfirmed; nothing is concluded."""
from __future__ import annotations

from dataclasses import dataclass

from prosemirror.model import Node

from engine.replay import load_schema

from .sources import ProvenanceSources

CHECKED_KINDS = ("quote", "coach", "import", "helper")
MIN_QUOTE_WORDS = 4

_QUOTE_MAP = {
    **{c: "'" for c in "‘’‚‛′`´"},
    **{c: '"' for c in "“”„‟″«»"},
}
_TRANS = str.maketrans(_QUOTE_MAP)


def normalise(text: str) -> str:
    return " ".join(text.translate(_TRANS).split())


def word_count(normalised: str) -> int:
    return len(normalised.split())


@dataclass(frozen=True)
class OriginRun:
    from_: int
    to: int
    kind: str
    ref: str | None
    text: str


def _origin_key(node: Node) -> tuple[str, str | None]:
    for m in node.marks:
        if m.type.name == "origin":
            return (m.attrs["kind"], m.attrs.get("ref"))
    return ("none", None)


def origin_runs(doc: Node | dict) -> list[OriginRun]:
    if not isinstance(doc, Node):
        doc = Node.from_json(load_schema(), doc)
    runs: list[OriginRun] = []

    def textblock(block: Node, start: int) -> None:
        cur: list | None = None  # [from, to, key, text]

        def close() -> None:
            nonlocal cur
            if cur is not None:
                runs.append(OriginRun(cur[0], cur[1], cur[2][0], cur[2][1], cur[3]))
            cur = None

        pos = start
        for child in block.content.content:
            key = _origin_key(child)
            end = pos + child.node_size
            if child.is_text:
                piece = child.text
            else:  # hard_break
                piece = "\n"
            if cur is not None and cur[2] == key:
                cur[1], cur[3] = end, cur[3] + piece
            elif child.is_text:
                close()
                cur = [pos, end, key, piece]
            else:
                close()
            pos = end
        close()

    def visit(node: Node, pos: int, parent, index) -> bool:
        if node.is_textblock:
            textblock(node, pos + 1)
            return False
        return True

    doc.descendants(visit)
    return runs


@dataclass(frozen=True)
class RunCheck:
    from_: int
    to: int
    kind: str
    ref: str | None
    confirmed: bool
    reason: str

    def to_json(self) -> dict:
        return {"from": self.from_, "to": self.to, "kind": self.kind, "ref": self.ref,
                "confirmed": self.confirmed, "reason": self.reason}


def _reason(run: OriginRun, sources: ProvenanceSources) -> str:
    if not run.ref:
        return "missing_ref"
    r = normalise(run.text)
    if run.kind == "quote":
        block = sources.block_text(run.ref)
        if block is None:
            return "origin_not_found"
        b = normalise(block)
        if r not in b:
            return "not_in_block"
        if r == b:
            return "ok"
        return "too_short" if word_count(r) < MIN_QUOTE_WORDS else "ok"
    if run.kind == "coach":
        a = sources.coach_answer(run.ref)
        if a is None:
            return "origin_not_found"
        if any(r in normalise(a.text[f:t]) for f, t in a.typed_ranges):
            return "ok"
        return "pasted_in_answer" if r in normalise(a.text) else "not_in_answer"
    if run.kind == "import":
        t = sources.import_text(run.ref)
        if t is None:
            return "origin_not_found"
        return "ok" if r in normalise(t) else "not_in_import"
    if run.kind == "helper":
        t = sources.helper_output(run.ref)
        if t is None:
            return "origin_not_found"
        return "ok" if r in normalise(t) else "not_in_output"
    return "ok"


def check_run(run: OriginRun, sources: ProvenanceSources) -> RunCheck:
    reason = _reason(run, sources)
    return RunCheck(run.from_, run.to, run.kind, run.ref, reason == "ok", reason)


def check_marks(doc, sources: ProvenanceSources) -> list[RunCheck]:
    return [check_run(r, sources) for r in origin_runs(doc) if r.kind in CHECKED_KINDS]
