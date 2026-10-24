"""Where the provenance engine looks up the material a mark points at (provenance.md section 4.1)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class CoachAnswer:
    text: str
    # [from, to) offsets into `text` (Python str indices) recorded as typed; the rest is pasted.
    typed_ranges: tuple[tuple[int, int], ...]


class ProvenanceSources(Protocol):
    def block_text(self, block_id: str) -> str | None: ...
    def coach_answer(self, q_id: str) -> CoachAnswer | None: ...
    def import_text(self, import_id: str) -> str | None: ...
    def helper_output(self, serve_id: str) -> str | None: ...


@dataclass
class InMemorySources:
    blocks: dict[str, str] = field(default_factory=dict)
    coach: dict[str, CoachAnswer] = field(default_factory=dict)
    imports: dict[str, str] = field(default_factory=dict)
    helper: dict[str, str] = field(default_factory=dict)

    def block_text(self, block_id: str) -> str | None:
        return self.blocks.get(block_id)

    def coach_answer(self, q_id: str) -> CoachAnswer | None:
        return self.coach.get(q_id)

    def import_text(self, import_id: str) -> str | None:
        return self.imports.get(import_id)

    def helper_output(self, serve_id: str) -> str | None:
        return self.helper.get(serve_id)


def coach_answer_from_runs(text: str, origin_runs: list[dict]) -> CoachAnswer:
    """Typed runs become typed ranges (clamped, merged); anything uncovered counts as pasted."""
    n = len(text)
    spans = []
    for r in origin_runs:
        if r.get("kind") != "typed":
            continue
        a, b = max(0, int(r["from"])), min(n, int(r["to"]))
        if a < b:
            spans.append((a, b))
    spans.sort()
    merged: list[list[int]] = []
    for a, b in spans:
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    return CoachAnswer(text, tuple((a, b) for a, b in merged))
