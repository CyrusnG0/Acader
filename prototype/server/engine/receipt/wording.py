"""The wording filter (receipt.md section 5, product law 10). Pure.

Case-insensitive stems. Conservative on purpose: "flagship" is caught by `flag`, and the
fallback text is used instead. A false positive costs a plain fallback; a miss costs trust.
"""
from __future__ import annotations

import re

_DASHES = "\\-\u2010-\u2015"

_PATTERNS = (
    ("detect", r"\bdetect\w*"),
    ("catch", r"\bcatch\w*|\bcaught\b"),
    ("cheat", r"\bcheat\w*"),
    ("ghost", r"\bghost\w*"),
    ("forensic", r"\bforensic\w*"),
    ("ai_generated", r"\bai[\s" + _DASHES + r"]*generated\b"),
    ("suspicious", r"\bsuspicio\w*"),
    ("suspect", r"\bsuspect\w*"),
    ("flag", r"\bflag\w*"),
    ("violation", r"\bviolat\w*"),
    ("integrity_score", r"\bintegrity\s+scor\w*"),
    ("probability", r"\bprobabilit\w*"),
    ("hundred_percent", r"\b100\s*%|\bone hundred per\s*cent\b|\bhundred percent\b"),
)

BANNED: tuple = tuple((name, re.compile(pat, re.IGNORECASE)) for name, pat in _PATTERNS)


def banned_hits(s: str) -> list:
    return [name for name, pat in BANNED if pat.search(s)]


def is_clean(s: str) -> bool:
    return not banned_hits(s)


class WordingFilter:
    """Replaces any unclean string with a clean fallback and counts the replacements."""

    def __init__(self):
        self.replaced = 0

    def apply(self, s: str, fallback: str) -> str:
        if is_clean(s):
            return s
        assert is_clean(fallback), "wording fallback must itself be clean"
        self.replaced += 1
        return fallback
