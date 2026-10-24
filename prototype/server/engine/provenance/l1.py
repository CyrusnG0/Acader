"""L1: deterministic provenance for one sealed log (provenance.md sections 3-7)."""
from __future__ import annotations

from dataclasses import dataclass

from engine.events import canonical_json

from .bands import L3bResult, NOTE_TEXT, analyse, walk_textblocks
from .compile import CompileResult
from .facts import compute_facts
from .markcheck import MIN_QUOTE_WORDS
from .trail import build_trail

L1_VERSION = 1


def _pct(name, v):
    if isinstance(v, bool) or not isinstance(v, int) or not 0 <= v <= 100:
        raise ValueError(f"{name} must be an int in 0..100")


@dataclass(frozen=True)
class L1Config:
    l3b: bool = False
    unlinked_untyped_pct: int = 30
    paste_ext_pct: int = 50
    declared_import_pct: int = 50
    min_quote_words: int = MIN_QUOTE_WORDS

    def __post_init__(self):
        if not isinstance(self.l3b, bool):
            raise ValueError("l3b must be a bool")
        for n in ("unlinked_untyped_pct", "paste_ext_pct", "declared_import_pct"):
            _pct(n, getattr(self, n))
        m = self.min_quote_words
        if isinstance(m, bool) or not isinstance(m, int) or m < 1:
            raise ValueError("min_quote_words must be an int >= 1")

    def to_json(self) -> dict:
        return {"flags": {"l3b": self.l3b},
                "thresholds": {"declared_import_pct": self.declared_import_pct,
                               "min_quote_words": self.min_quote_words,
                               "paste_ext_pct": self.paste_ext_pct,
                               "unlinked_untyped_pct": self.unlinked_untyped_pct}}


def compute_l1(doc, runs, events, *, seal_seq: int | None = None, block_kinds=None, l3b=(),
               config: L1Config = L1Config(), status: str = "complete",
               built_from: str = "replay") -> dict:
    l3b = tuple(l3b)
    if l3b and not config.l3b:
        raise ValueError("L3b results given while config.l3b is off")
    evs = sorted((e for e in events if seal_seq is None or e["seq"] <= seal_seq),
                 key=lambda e: e["seq"])
    trail = build_trail(evs)
    blocks = walk_textblocks(doc)
    suggestions = sum(1 for e in evs if e["type"] == "map.suggestion")
    out = {"l1_version": L1_VERSION, "status": status, "built_from": built_from,
           "engine": config.to_json()}
    out.update(analyse(blocks, runs, trail, config, l3b, suggestions))
    out["facts"] = compute_facts(evs, doc, trail, block_kinds=block_kinds or {},
                                 paste_ext_pct=config.paste_ext_pct)
    canonical_json(out)
    return out


def l1_from_compile(result: CompileResult, events, **kw) -> dict:
    return compute_l1(result.replay.doc, result.runs, events, seal_seq=result.replay.seal_seq,
                      status=result.status, built_from=result.replay.built_from, **kw)


__all__ = ["L1_VERSION", "L1Config", "L3bResult", "NOTE_TEXT", "compute_l1", "l1_from_compile"]
