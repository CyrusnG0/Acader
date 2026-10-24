"""The wording filter (receipt.md section 5, product law 10)."""
import pytest

from engine.receipt import copy
from engine.receipt.wording import BANNED, WordingFilter, banned_hits, is_clean


@pytest.mark.parametrize("text,name", [
    ("Detected", "detect"), ("detection of sepsis", "detect"),
    ("caught", "catch"), ("catching up", "catch"),
    ("cheating", "cheat"), ("no cheating", "cheat"),
    ("Ghostwriter", "ghost"),
    ("Forensic review", "forensic"),
    ("AI-generated", "ai_generated"), ("AI generated", "ai_generated"),
    ("ai–generated", "ai_generated"),
    ("suspicious", "suspicious"), ("suspected", "suspect"),
    ("flagged", "flag"), ("violations", "violation"),
    ("integrity score", "integrity_score"), ("probability", "probability"),
    ("100%", "hundred_percent"), ("100 %", "hundred_percent"),
    ("one hundred per cent", "hundred_percent"), ("hundred percent", "hundred_percent"),
])
def test_each_pattern_is_caught(text, name):
    assert name in banned_hits(text)
    assert not is_clean(text)


def test_all_thirteen_patterns_exist():
    assert len(BANNED) == 13
    assert len({n for n, _ in BANNED}) == 13


@pytest.mark.parametrize("text", ["traced", "untraced", "declared", "where to ask",
                                  "catalogue", "A paragraph about fluids", "100 words"])
def test_clean_words_pass(text):
    assert banned_hits(text) == []
    assert is_clean(text)


def test_flagship_is_caught_by_design():
    # conservative on purpose: a plain fallback is cheaper than a banned word on a receipt
    assert not is_clean("flagship product")


def test_apply_replaces_and_counts():
    wf = WordingFilter()
    assert wf.apply("fine text", "x") == "fine text"
    assert wf.replaced == 0
    assert wf.apply("GhostWriter Pro", copy.FALLBACK_TOOL) == copy.FALLBACK_TOOL
    assert wf.apply("Detecting sepsis", copy.FALLBACK_TITLE) == copy.FALLBACK_TITLE
    assert wf.replaced == 2


def test_fallback_must_be_clean():
    with pytest.raises(AssertionError):
        WordingFilter().apply("cheating", "flagged")


def test_every_copy_string_is_clean():
    def walk(v):
        if isinstance(v, str):
            yield v
        elif isinstance(v, dict):
            for x in v.values():
                yield from walk(x)
    for name in dir(copy):
        if name.isupper():
            for s in walk(getattr(copy, name)):
                assert is_clean(s), (name, s)
