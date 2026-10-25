"""T-027: "More places to ask" (receipt.md §2 item 3, §4; D-060).

The teacher receipt keeps the top 2-3 questions on the first screen. Every other grounded
candidate place the question step considered is kept in `more_places`, in paragraph order,
with the existing plain reason copy and no generated question text or provider call.
"""
from __future__ import annotations

import copy as pycopy
import functools
import json

import pytest

from app.receipt_service import issue_receipt
from engine.events import canonical_json, sha256_hex, verify
from engine.receipt import compile_receipt, copy as receipt_copy
from engine.receipt.questions import select_candidates
from engine.receipt.wording import banned_hits, is_clean
from golden.build import build_session
from golden.script import list_sessions, load_script
from golden.view_context import build_view_context
from tests.test_l1_bands import doc, para, run, t
from tests.test_receipt_compile import (FIXED_STAMP, Counting, banned_in, parts, rich_log,
                                        walk)

LOG = "L1"
MORE_KEYS = {"paragraph_id", "span", "why", "why_text", "grounding", "event_ids"}


# ---------------------------------------------------------------- fixtures / helpers
def five_place_log():
    """Five grounded candidates. Priority order is p5, p2, p3, p4, p1; paragraph order is
    p1, p2, p3, p4, p5. So the non-chosen places must be sorted by span, not by priority."""
    paras = [
        ("Opening point stands here.", ["k1"], "typed", None),
        ("Declared one point here.", ["kd"], "typed", None),
        ("Declared two point here.", ["kd2"], "typed", None),
        ("Declared three point here.", ["kd3"], "typed", None),
        ("Closing words stand here.", [], "typed", None),
    ]
    extra = [
        ("import.declared", "student", {"import_id": "i2", "tool_name": "ChatGPT",
                                        "raw_text_ref": "r2", "size_chars": 80}),
        ("claim.extracted", "system", {"claim_id": "kd2", "text": "Second outside claim",
                                       "import_id": "i2"}),
        ("import.declared", "student", {"import_id": "i3", "tool_name": "ChatGPT",
                                        "raw_text_ref": "r3", "size_chars": 80}),
        ("claim.extracted", "system", {"claim_id": "kd3", "text": "Third outside claim",
                                       "import_id": "i3"}),
    ]
    return rich_log(paras=paras, extra=extra)


def two_candidate_log():
    """Five places as above, but p1 (only in more_places) and p2 (chosen) each carry two
    grounded candidates: two student claims on p1, two declared claims on p2."""
    paras = [
        ("Opening point stands here.", ["k1", "k1b"], "typed", None),
        ("Declared one point here.", ["kd", "kd4"], "typed", None),
        ("Declared two point here.", ["kd2"], "typed", None),
        ("Declared three point here.", ["kd3"], "typed", None),
        ("Closing words stand here.", [], "typed", None),
    ]
    extra = [
        ("claim.create", "student", {"claim_id": "k1b", "text": "A second own claim",
                                     "card_ids": ["c1"], "parent_claim_id": None}),
        ("import.declared", "student", {"import_id": "i2", "tool_name": "ChatGPT",
                                        "raw_text_ref": "r2", "size_chars": 80}),
        ("claim.extracted", "system", {"claim_id": "kd2", "text": "Second outside claim",
                                       "import_id": "i2"}),
        ("import.declared", "student", {"import_id": "i3", "tool_name": "ChatGPT",
                                        "raw_text_ref": "r3", "size_chars": 80}),
        ("claim.extracted", "system", {"claim_id": "kd3", "text": "Third outside claim",
                                       "import_id": "i3"}),
        ("import.declared", "student", {"import_id": "i4", "tool_name": "ChatGPT",
                                        "raw_text_ref": "r4", "size_chars": 80}),
        ("claim.extracted", "system", {"claim_id": "kd4", "text": "Fourth outside claim",
                                       "import_id": "i4"}),
    ]
    return rich_log(paras=paras, extra=extra)


@functools.lru_cache(maxsize=None)
def golden_built(session_id: str):
    return build_session(session_id)


def receipt_for(*, ask=None):
    svc, sources = five_place_log()
    res, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP, ask=ask)
    return res, svc.events(LOG)


def full_candidates(res):
    """Ground truth: every grounded candidate, with no limit."""
    return select_candidates(res.l1, res.receipt_events, res.doc, seal_seq=res.seal_seq,
                             sources=res.sources, limit=1000)[0]


# ---------------------------------------------------------------- candidate selection
def test_more_places_are_exactly_the_grounded_non_chosen_candidates_in_paragraph_order():
    svc, sources = five_place_log()
    p = parts(svc, sources)
    chosen, more, skipped = select_candidates(p["l1"], p["events"], p["doc"], seal_seq=999,
                                              sources=sources, limit=3)
    # Top three are exactly what the pre-T-027 limit=3 selection returned.
    assert [(c["why"], c["paragraph_id"]) for c in chosen] == [
        ("untraced_claim", "p5"), ("declared_not_anchored", "p2"),
        ("declared_not_anchored", "p3")]
    # The remaining grounded candidates, in paragraph (document) order, not priority order.
    assert [(c["why"], c["paragraph_id"]) for c in more] == [
        ("student_linked_claim", "p1"), ("declared_not_anchored", "p4")]
    assert [c["span"]["from"] for c in more] == sorted(c["span"]["from"] for c in more)
    assert skipped == 0
    assert all(c["grounding_items"] for c in more)
    assert len({c["paragraph_id"] for c in chosen + more}) == 5


def test_candidates_without_grounding_are_only_counted_and_never_listed():
    # No claims, cards or blocks at all: nothing can be cited (law 2).
    from engine.provenance import InMemorySources
    d = doc(para(t("First point stands here.")), para(t("Closing words stand here.")))
    sources = InMemorySources(blocks={})
    l1 = run(d, [], sources)
    chosen, more, skipped = select_candidates(l1, [], d, seal_seq=999, sources=sources)
    assert chosen == [] and more == []
    assert skipped == 2


def claim_units_for(l1, paragraph_id):
    sents = {s["id"]: s for s in l1["sentences"]}
    return [u for u in l1["claims"]
            if {sents[sid]["paragraph_id"] for sid in u["sentence_ids"]} == {paragraph_id}]


def test_one_place_per_paragraph_never_repeats():
    svc, sources = two_candidate_log()
    l1 = parts(svc, sources)["l1"]
    res, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP)
    chosen = {q["paragraph_id"] for q in res.receipt["questions"]}
    pids = [p["paragraph_id"] for p in res.receipt["more_places"]]
    # The fixture has two grounded candidates for p2 (chosen) and for p1 (not chosen).
    assert len(claim_units_for(l1, "p2")) == 2
    assert len(claim_units_for(l1, "p1")) == 2
    assert "p2" in chosen and "p1" in pids
    # At most one place per paragraph, and never one that already produced a question.
    assert len(pids) == len(set(pids))
    assert not (set(pids) & chosen)


# ---------------------------------------------------------------- compiled receipt
def test_more_places_hold_place_reason_grounding_and_events_only():
    res, _ = receipt_for()
    more = res.receipt["more_places"]
    assert len(more) == 2
    assert [p["paragraph_id"] for p in more] == ["p1", "p4"]
    for place in more:
        assert set(place) == MORE_KEYS
        assert set(place["span"]) == {"from", "to"}
        assert place["span"]["from"] < place["span"]["to"]
        assert place["why"] in receipt_copy.WHY_TEXT
        assert place["why_text"] == receipt_copy.WHY_TEXT[place["why"]]
        assert place["grounding"] and all(isinstance(i, str) for i in place["grounding"])
        assert place["event_ids"] and place["event_ids"] == sorted(set(place["event_ids"]))
        assert all(isinstance(i, int) and not isinstance(i, bool) for i in place["event_ids"])


def test_extra_places_get_no_generated_wording_and_no_extra_provider_call():
    ask = Counting()
    res, _ = receipt_for(ask=ask)
    # exactly one call per top question; the extra places never reach the model
    assert ask.calls == len(res.receipt["questions"]) == 3
    for place in res.receipt["more_places"]:
        assert "q" not in place and "pillar" not in place and "artifact_ids" not in place
    assert all(q["q"] for q in res.receipt["questions"])


def test_top_three_questions_are_unchanged():
    res, _ = receipt_for()
    assert [(q["why"], q["paragraph_id"]) for q in res.receipt["questions"]] == [
        ("untraced_claim", "p5"), ("declared_not_anchored", "p2"),
        ("declared_not_anchored", "p3")]
    assert [q["why_text"] for q in res.receipt["questions"]] == [
        receipt_copy.WHY_TEXT[q["why"]] for q in res.receipt["questions"]]


def test_more_places_has_no_floats_and_hashes_canonically():
    res, _ = receipt_for()
    assert not [value for path, value in walk(res.receipt) if isinstance(value, float)]
    canonical_json(res.receipt)
    assert res.receipt_hash == sha256_hex(canonical_json(res.receipt))


def test_receipt_hash_covers_the_new_field():
    res, events = receipt_for()
    tampered = pycopy.deepcopy(res.receipt)
    tampered["more_places"][0]["why_text"] += " Edited."
    assert sha256_hex(canonical_json(tampered)) != res.receipt_hash
    checked = verify(events, res.receipt["seal_hash"], receipt=tampered,
                     artifacts=res.artifacts)
    assert not checked.ok
    assert any("receipt_hash" in problem for problem in checked.problems)
    # Adding or removing the field is a different canonical body.
    without = pycopy.deepcopy(res.receipt)
    without.pop("more_places")
    assert sha256_hex(canonical_json(without)) != res.receipt_hash


def test_recompile_and_stored_replay_are_byte_identical():
    svc, sources = five_place_log()
    first, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP)
    second, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP)
    assert canonical_json(first.receipt) == canonical_json(second.receipt)
    stored = compile_receipt(ask=None, stored=first.artifacts, **parts(svc, sources))
    assert canonical_json(stored.receipt) == canonical_json(first.receipt)
    assert stored.receipt_hash == first.receipt_hash
    assert first.receipt["more_places"]


# ---------------------------------------------------------------- wording (law 10)
def test_every_new_string_passes_the_wording_filter():
    res, _ = receipt_for()
    strings = []
    for place in res.receipt["more_places"]:
        for key, value in place.items():
            if key in ("why", "grounding"):
                continue  # internal codes and ids, as in `questions`
            strings.append(value if isinstance(value, str) else json.dumps(value))
    assert strings
    assert not [s for s in strings if banned_hits(s)]
    assert all(is_clean(s) for s in strings)
    assert banned_in(res.receipt) == []
    assert res.receipt["engine"]["wording_filter"]["replaced"] == 0


def test_wording_sweep_covers_the_new_reason_text(monkeypatch):
    monkeypatch.setitem(receipt_copy.WHY_TEXT, "declared_not_anchored", "This was flagged.")
    res, _ = receipt_for()
    places = res.receipt["more_places"]
    assert places
    assert all(p["why_text"] == receipt_copy.FALLBACK_TEXT for p in places
               if p["why"] == "declared_not_anchored")
    # The same copy feeds the chosen questions and the extra places, and every count is swept.
    declared = [item for item in res.receipt["questions"] + places
                if item["why"] == "declared_not_anchored"]
    assert len(declared) == 3
    assert res.receipt["engine"]["wording_filter"]["replaced"] == len(declared)
    assert banned_in(res.receipt) == []


# ---------------------------------------------------------------- golden receipts
@pytest.mark.parametrize("session_id", list_sessions())
def test_golden_receipts_list_exactly_the_non_chosen_grounded_candidates(session_id):
    res = golden_built(session_id)
    full = full_candidates(res)
    from engine.receipt.questions import select_candidates as sc
    more, skipped = sc(res.l1, res.receipt_events, res.doc, seal_seq=res.seal_seq,
                       sources=res.sources, limit=1000)[1:]
    assert skipped == 0
    # Top three unchanged: exactly the first three of the full grounded priority list.
    assert [q["paragraph_id"] for q in res.receipt["questions"]] == [
        c["paragraph_id"] for c in full[:3]]
    expected = [{
        "paragraph_id": c["paragraph_id"], "span": dict(c["span"]),
        "why": c["why"], "why_text": receipt_copy.WHY_TEXT[c["why"]],
        "grounding": [i["id"] for i in c["grounding_items"]],
        "event_ids": list(c["event_ids"]),
    } for c in more]
    assert res.receipt["more_places"] == expected
    assert [p["span"]["from"] for p in res.receipt["more_places"]] == sorted(
        p["span"]["from"] for p in res.receipt["more_places"])


@pytest.mark.parametrize("session_id", list_sessions())
def test_golden_recompile_with_the_new_field_is_byte_identical_and_verifies(session_id):
    res = golden_built(session_id)
    replayed = compile_receipt(events=res.receipt_events, l1=res.l1, doc=res.doc,
                               log_id=session_id, seal_hash=res.seal, sources=res.sources,
                               stamp=res.stamp, ask=None, stored=res.artifacts)
    assert canonical_json(replayed.receipt) == canonical_json(res.receipt)
    assert replayed.receipt_hash == res.receipt_hash
    assert sha256_hex(canonical_json(res.receipt)) == res.receipt_hash
    assert verify(res.receipt_events, res.seal, receipt=res.receipt,
                  artifacts=res.artifacts).ok


# ---------------------------------------------------------------- student boundary (OL-059)
def test_student_view_context_does_not_contain_the_more_places_list():
    session_id = "honest-nursing"
    res = golden_built(session_id)
    context = build_view_context(res, load_script(session_id), 0)
    body = json.dumps(context, ensure_ascii=False)
    assert "more_places" not in context
    assert "More places to ask" not in body
    # The receipt is the teacher artifact; the existing student view never receives it.
    assert not [value for value in context.values() if isinstance(value, dict)
                and "more_places" in value]
