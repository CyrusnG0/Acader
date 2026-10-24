"""Sentence split for one textblock (provenance.md section 3). Pure; returns [start, end) offsets."""
from __future__ import annotations

import re

TERMINATORS = ".!?…"
CLOSERS = "\"'”’)]»"
OPENERS = "\"'“‘([«"

NO_BREAK = frozenset({
    "e.g.", "i.e.", "cf.", "vs.", "al.", "approx.", "ca.", "fig.", "figs.", "eq.", "no.", "nos.",
    "vol.", "pp.", "p.", "ch.", "sec.", "dr.", "mr.", "mrs.", "ms.", "prof.", "st.", "jr.", "sr.",
    "ed.", "eds."})

_INITIALS = re.compile(r"^(?:[^\W\d_]\.)+$")
_DIGITS = re.compile(r"^\d+\.$")


def words(text: str) -> int:
    return len(text.split())


def _next_char(text: str, i: int, end: int) -> str | None:
    """Next non-whitespace char at or after i, after skipping opening chars."""
    while i < end and (text[i].isspace() or text[i] in OPENERS):
        i += 1
    return text[i] if i < end else None


def _no_break_token(text: str, dot: int, first_nonws: int) -> bool:
    s = dot
    while s > 0 and not text[s - 1].isspace():
        s -= 1
    low = text[s:dot + 1].lower()
    i = 0
    while i < len(low) and low[i] in OPENERS:
        i += 1
    low = low[i:]
    if low in NO_BREAK:
        return True
    if _INITIALS.match(low):
        # A lone initial after a plain lowercase word ("found X.") ends the sentence; the spec's
        # required case "Smith et al. (2019) found X. Next one." gives two sentences.
        if len(low) == 2:
            prev = text[:s].split()
            if prev and prev[-1].isalpha() and prev[-1].islower():
                return False
        return True
    if _DIGITS.match(low) and s + i == first_nonws:
        return True
    return False


def _trim(text: str, a: int, b: int) -> tuple[int, int] | None:
    while a < b and text[a].isspace():
        a += 1
    while b > a and text[b - 1].isspace():
        b -= 1
    return (a, b) if a < b else None


def split_sentences(text: str) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    first_nonws = next((i for i, c in enumerate(text) if not c.isspace()), len(text))
    line_start = 0
    lines: list[tuple[int, int]] = []
    for i, c in enumerate(text):
        if c == "\n":
            lines.append((line_start, i))
            line_start = i + 1
    lines.append((line_start, len(text)))
    for ls, le in lines:
        start = ls
        i = ls
        while i < le:
            if text[i] not in TERMINATORS:
                i += 1
                continue
            j = i
            while j < le and text[j] in TERMINATORS:
                j += 1
            k = j
            while k < le and text[k] in CLOSERS:
                k += 1
            if not (k == le or text[k].isspace()):
                i = k
                continue
            nxt = _next_char(text, k, le)
            if nxt is not None and nxt.islower():
                i = k
                continue
            if j - i == 1 and text[i] == "." and _no_break_token(text, i, first_nonws):
                i = k
                continue
            span = _trim(text, start, k)
            if span:
                out.append(span)
            start = k
            i = k
        span = _trim(text, start, le)
        if span:
            out.append(span)
    return out
