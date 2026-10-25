"""Questions worth asking: candidates, grounding, prompt, output check, asking loop."""
import json

import pytest

from engine.events import canonical_json, sha256_hex
from engine.provenance import InMemorySources
from engine.receipt import copy
from engine.receipt.questions import (ABOUT_THE_TRACE, ASKS_ORIGIN, CONSTRUCTION_ORDER,
                                      LLMUnavailable, OutputRejected, ask_question,
                                      build_messages, make_artifact, prompt_file_hash,
                                      prompt_hash, select_candidates, validate_output)
from tests.test_l1_bands import (BLOCK, card_events, claim_ev, doc, ev, link, para, run, t,
                                 typed_runs)

SRC = InMemorySources(blocks={"b1": BLOCK})
GOOD = {"question": "What would you say to a reader who thinks this reading proves less?",
        "pillar": "communication", "cites": ["g1"]}


# ---------------------------------------------------------------- validate_output
def bad(**kw):
    return {**GOOD, **kw}


@pytest.mark.parametrize("out,reason", [
    ("text", "shape"), ({"question": "x"}, "shape"), ({**GOOD, "extra": 1}, "shape"),
    (bad(cites="g1"), "shape"), (bad(cites=[1]), "shape"), (bad(question=3), "shape"),
    (bad(pillar="vibes"), "pillar"),
    (bad(cites=[]), "cites"), (bad(cites=["g9"]), "cites"), (bad(cites=["g1", "g9"]), "cites"),
    (bad(question="Tell me about the reading in detail."), "not_a_question"),
    (bad(question="Why?"), "length"),
    (bad(question=" ".join(["word"] * 31) + "?"), "length"),
    (bad(question="Was this finding flagged by the reading you chose?"), "wording"),
    (bad(question="How did you think of this claim about fluids?"), "asks_origin"),
    (bad(question="Where did this idea come from in the reading?"), "asks_origin"),
    (bad(question="Which came first, the card or the sentence you chose?"), "construction_order"),
    (bad(question="Is the outline first or the paragraph you wrote?"), "construction_order"),
    (bad(question="Did you write this paragraph before your card?"), "about_the_trace"),
    (bad(question="Was this passage pasted from somewhere else entirely?"), "about_the_trace"),
])
def test_validate_reasons(out, reason):
    assert validate_output(out, {"g1", "g2"}) == reason


def test_good_and_stub_fixture_pass():
    assert validate_output(GOOD, {"g1"}) is None
    from app.llm import STUB_FIXTURES, Task
    assert validate_output(STUB_FIXTURES[Task.receipt_question], {"g1"}) is None


def test_origin_example_and_trace_example():
    q = lambda s: validate_output(bad(question=s), {"g1"})
    assert q("How did you think of this?") == "asks_origin"
    assert q("Did you write this paragraph before your card?") in ("about_the_trace",
                                                                   "construction_order")


def test_regexes_are_named_constants():
    assert ASKS_ORIGIN.flags and CONSTRUCTION_ORDER.flags and ABOUT_THE_TRACE.flags


# ---------------------------------------------------------------- candidates
def para_linked(text, *ids):
    return para(t(text), links=[link(i) for i in ids])


def cands(d, events, **kw):
    l1 = run(d, events, SRC)
    return select_candidates(l1, events, d, seal_seq=999, sources=SRC, **kw)


def base_events():
    return card_events(1) + [claim_ev(3)] + [
        ev(4, "source.add", source_id="s1", origin="teacher", title="Fluid balance study")]


def test_rule_order_and_at_most_three():
    d = doc(para_linked("First point stands here.", "k1"),
            para_linked("Second point stands here.", "kd"),
            para(t("Closing words stand here.")))
    evs = base_events() + [ev(5, "claim.extracted", claim_id="kd", text="Outside claim",
                              import_id="i1")]
    out, _, skipped = cands(d, evs)
    assert [c["why"] for c in out] == ["untraced_claim", "declared_not_anchored",
                                       "student_linked_claim"]
    assert [c["paragraph_id"] for c in out] == ["p3", "p2", "p1"]
    assert skipped == 0
    assert [c["paragraph_number"] for c in out] == [3, 2, 1]
    assert all(c["span"]["from"] < c["span"]["to"] for c in out)


def test_limit_three_even_with_more_candidates():
    paras = [para_linked("First point stands here.", "k1")]
    evs = base_events()
    for n in (2, 3, 4):
        paras.append(para_linked(f"Declared point {n} here.", f"kd{n}"))
        evs.append(ev(10 + n, "claim.extracted", claim_id=f"kd{n}", text=f"Outside {n}",
                      import_id=f"i{n}"))
    paras.append(para(t("Closing words stand here.")))
    out, _, _ = cands(doc(*paras), evs)
    assert len(out) == 3
    assert [c["why"] for c in out] == ["untraced_claim", "declared_not_anchored",
                                       "declared_not_anchored"]
    assert [c["paragraph_id"] for c in out] == ["p5", "p2", "p3"]


def test_at_most_one_candidate_per_paragraph():
    d = doc(para_linked("First point stands here.", "k1"),
            para_linked("Both declared claims sit here.", "kd1", "kd2"),
            para_linked("Third point stands here.", "k1"))
    evs = base_events() + [
        ev(5, "claim.extracted", claim_id="kd1", text="Outside one", import_id="i1"),
        ev(6, "claim.extracted", claim_id="kd2", text="Outside two", import_id="i2")]
    out, _, _ = cands(d, evs)
    pids = [c["paragraph_id"] for c in out]
    assert len(pids) == len(set(pids))
    assert pids.count("p2") == 1


def test_middle_untraced_unit_needs_dependents():
    d = doc(para_linked("First point stands here.", "k1"),
            para(t("Pasted middle passage here.", "paste_ext", "pp1"), links=[link("km")]),
            para_linked("Last point stands here.", "k1"))
    evs = base_events() + [claim_ev(5, "km", ())]
    out, _, _ = cands(d, evs)
    assert "p2" not in [c["paragraph_id"] for c in out]
    child = ev(7, "claim.create", claim_id="kc", text="child claim", card_ids=["c1"],
               parent_claim_id="km")
    out, _, _ = cands(d, evs + [child])
    assert [c["why"] for c in out if c["paragraph_id"] == "p2"] == ["untraced_claim"]


def test_unit_without_grounding_is_skipped_and_counted():
    d = doc(para_linked("First point stands here.", "k1"),
            para(t("Closing words stand here.")))
    # no claims, cards or blocks at all: the unlinked closing paragraph has nothing to cite
    out, _, skipped = cands(d, [])
    assert out == [] and skipped == 2  # the linked intro (claim unknown) and the closing paragraph


def test_grounding_items_for_unlinked_and_linked_units():
    d = doc(para_linked("First point stands here.", "k1"),
            para(t("Closing words stand here.")))
    out, _, _ = cands(d, base_events())
    last = next(c for c in out if c["paragraph_id"] == "p2")
    assert [(i["label"], i["kind"], i["id"]) for i in last["grounding_items"]] == [
        ("g1", "claim", "k1"), ("g2", "block", "b1")]
    assert last["grounding_items"][1]["title"] == "Fluid balance study"
    assert last["grounding_items"][1]["text"] == BLOCK
    first = next(c for c in out if c["paragraph_id"] == "p1")
    assert first["claim_id"] == "k1"
    assert [i["id"] for i in first["grounding_items"]] == ["k1", "b1"]
    assert 999 in first["event_ids"] and first["event_ids"] == sorted(set(first["event_ids"]))
    assert {1, 2, 3} <= set(first["event_ids"])


def test_grounding_is_capped_and_truncated():
    long = "word " * 200
    srcs = InMemorySources(blocks={f"b{i}": long for i in range(8)})
    evs = [ev(1, "card.create", card_id="c1", text="a card", origin_runs=typed_runs("a card"),
              via="typed", via_ref=None)]
    evs += [ev(2 + i, "card.anchor", card_id="c1", source_id="s1", block_id=f"b{i}")
            for i in range(8)]
    evs.append(claim_ev(20))
    d = doc(para_linked("First point stands here.", "k1"))
    l1 = run(d, evs, srcs)
    out, _, _ = select_candidates(l1, evs, d, seal_seq=99, sources=srcs)
    items = out[0]["grounding_items"]
    assert len(items) == 6 and [i["label"] for i in items] == [f"g{n}" for n in range(1, 7)]
    assert all(len(i["text"]) <= 400 for i in items)


def finding_setup(kind="unconnected_paragraph", claim_id=None):
    d = doc(para_linked("First point stands here.", "k1"),
            para(t("Middle words stand here.")),
            para_linked("Last point stands here.", "k1"))
    l1 = run(d, base_events(), SRC)
    p2 = next(p for p in l1["paragraphs"] if p["id"] == "p2")
    payload = {"finding_id": "f1", "kind": kind, "span": {"from": p2["from"], "to": p2["to"]},
               "artifact_id": "a_map1"}
    if claim_id:
        payload["claim_id"] = claim_id
    return d, base_events() + [ev(30, "map.finding", **payload)]


def finding_cands(d, evs):
    out, _, _ = cands(d, evs)
    return [c for c in out if c["why"].startswith("map_finding")]


def test_map_finding_candidate_and_its_fields():
    d, evs = finding_setup()
    (f,) = finding_cands(d, evs)
    assert f["why"] == "map_finding_unconnected_paragraph" and f["paragraph_id"] == "p2"
    assert f["source_artifact_ids"] == ["a_map1"] and 30 in f["event_ids"]


def test_map_finding_answered_by_coach_outcome_is_skipped():
    d, evs = finding_setup()
    ask_ev = ev(31, "coach.ask", q_id="q1", case="B", trigger_ref="f1", pillar="logic")
    assert len(finding_cands(d, evs + [ask_ev])) == 1  # asked, not answered
    out_ev = ev(32, "coach.outcome", q_id="q1", outcome="answered", answer_text="x")
    assert finding_cands(d, evs + [ask_ev, out_ev]) == []


def test_map_finding_on_paragraph_answered_not_this_is_skipped():
    d, evs = finding_setup()
    sg = ev(31, "map.suggestion", suggestion_id="sg1", paragraph="p2", claim_id="k1")
    assert len(finding_cands(d, evs + [sg, ev(32, "map.answer", suggestion_id="sg1",
                                              answer="yes")])) == 1
    assert finding_cands(d, evs + [sg, ev(32, "map.answer", suggestion_id="sg1",
                                          answer="no")]) == []


def test_map_finding_unconnected_needs_no_links_now():
    d, evs = finding_setup()
    linked = doc(para_linked("First point stands here.", "k1"),
                 para_linked("Middle words stand here.", "k1"),
                 para_linked("Last point stands here.", "k1"))
    assert finding_cands(linked, evs) == []


def test_map_finding_claim_without_source():
    d = doc(para_linked("First point stands here.", "k1"),
            para_linked("Middle words stand here.", "km"),
            para_linked("Last point stands here.", "k1"))
    base = card_events(1) + [claim_ev(3)]
    unanchored = card_events(10, "c2", anchored=False) + [claim_ev(12, "km", ("c2",))]
    evs = base + unanchored
    l1 = run(d, evs, SRC)
    p2 = next(p for p in l1["paragraphs"] if p["id"] == "p2")
    fnd = ev(40, "map.finding", finding_id="f9", kind="claim_without_source", claim_id="km",
             span={"from": p2["from"], "to": p2["to"]})
    out, _, _ = select_candidates(l1, evs + [fnd], d, seal_seq=99, sources=SRC)
    got = [c for c in out if c["why"] == "map_finding_claim_without_source"]
    assert len(got) == 1 and got[0]["claim_id"] == "km"
    # a claim that ends in a block is not "without a source"
    anchored = card_events(10, "c2") + [claim_ev(12, "km", ("c2",))]
    l1 = run(d, base + anchored, SRC)
    out, _, _ = select_candidates(l1, base + anchored + [fnd], d, seal_seq=99, sources=SRC)
    assert not [c for c in out if c["why"].startswith("map_finding")]


def test_events_after_the_seal_are_ignored():
    d, evs = finding_setup()
    out, _, _ = select_candidates(run(d, evs, SRC), evs, d, seal_seq=29, sources=SRC)
    assert not [c for c in out if c["why"].startswith("map_finding")]


# ---------------------------------------------------------------- prompt
def sample_candidate():
    d = doc(para_linked("First point stands here.", "k1"), para(t("Closing words stand here.")))
    out, _, _ = cands(d, base_events())
    return next(c for c in out if c["paragraph_id"] == "p2")


def test_build_messages_shape_and_no_why_leak():
    c = sample_candidate()
    m = build_messages(c, "The closing passage.", None)
    assert [x["role"] for x in m] == ["system", "user"]
    assert "paragraph 2 of the student's work" in m[1]["content"]
    assert "The closing passage." in m[1]["content"]
    assert 'g1 (a claim from the student\'s claim map): "a claim"' in m[1]["content"]
    assert 'g2 (a passage from the reading "Fluid balance study")' in m[1]["content"]
    assert c["why"] not in json.dumps(m) and "$" not in m[1]["content"]
    assert "could not be used" not in m[1]["content"]
    retry = build_messages(c, "x", "asks_origin")
    assert copy.RETRY_NOTE.format(reason="asks_origin") in retry[1]["content"]
    assert len(build_messages(c, "y" * 5000, None)[1]["content"]) < 4000


def test_prompt_hash_helpers():
    assert prompt_file_hash() == sha256_hex(
        (__import__("engine.receipt.questions", fromlist=["x"]).PROMPT_PATH).read_bytes())
    m = build_messages(sample_candidate(), "p", None)
    assert prompt_hash(m) == sha256_hex(canonical_json(m))
    a = make_artifact("receipt_question", "h", "{}")
    assert a["hash"] == sha256_hex(b"{}") and a["artifact_id"].startswith("a_")
    assert len(a["artifact_id"]) == 26


# ---------------------------------------------------------------- asking
class Script:
    def __init__(self, *replies):
        self.replies, self.calls = list(replies), 0

    def __call__(self, messages):
        self.calls += 1
        r = self.replies.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


def go(ask, stored=None, down=False):
    return ask_question(sample_candidate(), "passage", ask, stored or {}, llm_down=down)


def test_first_attempt_ok():
    q, arts, down = go(Script(GOOD))
    assert q == {"q": GOOD["question"], "pillar": "communication", "grounding": ["k1"]}
    assert len(arts) == 1 and not down


def test_cites_map_to_ids_in_label_order_unique():
    out = {**GOOD, "cites": ["g2", "g1", "g2"]}
    q, _, _ = go(Script(out))
    assert q["grounding"] == ["k1", "b1"]


def test_invalid_then_valid_keeps_both_artifacts():
    s = Script(bad(question="How did you think of this claim about fluids?"), GOOD)
    q, arts, _ = go(s)
    assert q is not None and len(arts) == 2 and s.calls == 2


def test_invalid_twice_is_unanswered_not_down():
    s = Script(bad(cites=["g7"]), bad(pillar="x"))
    q, arts, down = go(s)
    assert q is None and len(arts) == 2 and not down


def test_retry_reason_reaches_second_prompt():
    seen = []

    def ask(messages):
        seen.append(messages[1]["content"])
        return bad(cites=["g7"]) if len(seen) == 1 else GOOD
    go(ask)
    assert "reason: cites" in seen[1] and "reason" not in seen[0]


def test_output_rejected_counts_as_schema_without_artifact():
    s = Script(OutputRejected("bad json"), GOOD)
    seen = []
    q, arts, down = go(s)
    assert q is not None and len(arts) == 1 and not down


def test_llm_unavailable_and_none():
    q, arts, down = go(Script(LLMUnavailable("down")))
    assert (q, arts, down) == (None, [], True)
    assert go(None) == (None, [], True)
    s = Script(GOOD)
    assert go(s, down=True) == (None, [], True) and s.calls == 0


def test_stored_artifacts_are_reused_without_a_call():
    c = sample_candidate()
    m = build_messages(c, "passage", None)
    art = make_artifact("receipt_question", prompt_hash(m), canonical_json(GOOD).decode())
    s = Script()
    q, arts, down = go(s, {("receipt_question", prompt_hash(m)): art})
    assert q is not None and arts == [art] and s.calls == 0 and not down


def test_float_output_is_rejected_not_crashed():
    s = Script({**GOOD, "extra": 1.5}, GOOD)
    q, arts, _ = go(s)
    assert q is not None and len(arts) == 1
