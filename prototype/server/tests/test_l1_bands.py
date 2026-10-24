"""L1 mix, chains, bands, claim units, proportions, L3b queue, determinism (provenance.md 3-6)."""
import pytest

from engine.events import canonical_json
from engine.provenance import (CoachAnswer, InMemorySources, L1Config, L3bResult, check_marks,
                               compile_marks, compute_l1, l1_from_compile)

BLOCK = "The quick brown fox jumps over the lazy dog"
QUOTE = "quick brown fox jumps"
T = "2026-11-02T14:00:00Z"


# ---------------------------------------------------------------- builders
def mk(kind, ref=None):
    return {"type": "origin", "attrs": {"kind": kind, "ref": ref}}


def t(text, kind=None, ref=None):
    node = {"type": "text", "text": text}
    if kind:
        node["marks"] = [mk(kind, ref)]
    return node


def para(*inline, links=()):
    return {"type": "paragraph", "attrs": {"links": list(links)}, "content": list(inline)}


def heading(*inline):
    return {"type": "heading", "attrs": {"level": 1}, "content": list(inline)}


def doc(*blocks):
    return {"type": "doc", "content": list(blocks)}


def link(claim_id, by="student", suggestion_id=None):
    d = {"claim_id": claim_id, "by": by}
    if suggestion_id:
        d["suggestion_id"] = suggestion_id
    return d


_seq = [0]


def ev(seq, type_, **payload):
    return {"seq": seq, "type": type_, "payload": payload, "ts": T}


def typed_runs(text):
    return [{"from": 0, "to": len(text), "kind": "typed"}]


def card_events(seq, card_id="c1", text="a card", via="typed", via_ref=None, anchored=True,
                runs=None):
    out = [ev(seq, "card.create", card_id=card_id, text=text,
              origin_runs=typed_runs(text) if runs is None else runs, via=via, via_ref=via_ref)]
    if anchored:
        out.append(ev(seq + 1, "card.anchor", card_id=card_id, source_id="s1", block_id="b1"))
    return out


def claim_ev(seq, claim_id="k1", cards=("c1",)):
    return ev(seq, "claim.create", claim_id=claim_id, text="a claim", card_ids=list(cards),
              parent_claim_id=None)


def run(d, events=(), sources=None, **kw):
    s = sources or InMemorySources(blocks={"b1": BLOCK})
    return compute_l1(d, check_marks(d, s), list(events), **kw)


def band_of(out, i=0):
    return out["sentences"][i]["band"]


def anchored_claim_events():
    return card_events(1) + [claim_ev(3)]


def fraction_sentence(kind, k, ref=None, total=100):
    """One sentence of `total` chars: k chars marked `kind`, the rest typed."""
    return [t("a" * k, kind, ref), t("b" * (total - k - 1) + ".")]


# ---------------------------------------------------------------- band 1
def test_declared_by_import_chars_boundary():
    s = InMemorySources(imports={"i1": "a" * 50})
    out = run(doc(para(*fraction_sentence("import", 50, "i1"))), sources=s)
    assert band_of(out) == "declared"
    s = InMemorySources(imports={"i1": "a" * 49})
    out = run(doc(para(*fraction_sentence("import", 49, "i1"))), sources=s)
    assert band_of(out) == "untraced"


def test_declared_claim_not_reanchored_then_reanchored():
    d = doc(para(t("My own words here."), links=[link("k1")]))
    base = [ev(1, "claim.extracted", claim_id="k1", text="x", **{"from": "import"}, import_id="i1")]
    out = run(d, base)
    assert band_of(out) == "declared"
    assert out["claims"][0]["band"] == "declared" and out["claims"][0]["claim_kind"] == "declared"
    assert out["sentences"][0]["chains"][0]["ends"] == ["import"]
    more = base + card_events(2) + [ev(4, "claim.edit", claim_id="k1", text="x", card_ids=["c1"],
                                       parent_claim_id=None)]
    out = run(d, more)
    assert band_of(out) == "student_linked"
    assert out["claims"][0]["band"] == "student_linked"
    assert out["claims"][0]["claim_kind"] == "declared"
    assert out["bands"]["by_claims"]["declared"] == 0


# ---------------------------------------------------------------- bands 2 and 3
def test_traced_source_by_checked_quote():
    out = run(doc(para(t("As the text says "), t(QUOTE, "quote", "b1"), t(" in full."))))
    sent = out["sentences"][0]
    assert sent["band"] == "traced_source" and sent["quoted_words"] == 4
    assert sent["marks"] == [{"kind": "quote", "ref": "b1", "confirmed": True, "reason": "ok"}]
    assert out["bands"]["quoted_words"] == 4


def test_quote_plus_some_paste_is_not_traced():
    out = run(doc(para(t(QUOTE, "quote", "b1"), t(" and "), t("zzz", "paste_ext", "p1"),
                       t(" more."))))
    assert band_of(out) == "untraced"


def _coach_sources():
    text = "Pasted opening. My own typed thought."
    return InMemorySources(
        blocks={"b1": BLOCK},
        coach={"q1": CoachAnswer(text, ((16, len(text)),))})


def test_traced_coach_by_checked_mark():
    out = run(doc(para(t("As I said: "), t("My own typed thought", "coach", "q1"), t("."))),
              sources=_coach_sources())
    assert band_of(out) == "traced_coach"


def test_coach_run_on_pasted_part_is_unconfirmed():
    out = run(doc(para(t("As I said: "), t("Pasted opening", "coach", "q1"), t("."))),
              sources=_coach_sources())
    s = out["sentences"][0]
    assert s["band"] == "untraced" and s["mix"]["unconfirmed"] == 14 and s["mix"]["coach"] == 0
    assert s["notes"] == ["label_not_confirmed"]


def test_order_import_over_quote_and_source_over_coach():
    s = InMemorySources(blocks={"b1": BLOCK}, imports={"i1": "a" * 60})
    d = doc(para(t("a" * 60, "import", "i1"), t(" " + QUOTE, "quote", "b1"), t(".")))
    assert band_of(run(d, sources=s)) == "declared"
    s = _coach_sources()
    d = doc(para(t("My own typed thought", "coach", "q1"), t(" "), t(QUOTE, "quote", "b1"),
                 t(" end.")))
    assert band_of(run(d, sources=s)) == "traced_source"


# ---------------------------------------------------------------- D27 / D19 / L3b
LINKED = doc(para(t("Typed words about the claim."), links=[link("k1")]))


def test_d27_student_link_with_anchored_card_is_student_linked():
    out = run(LINKED, anchored_claim_events())
    assert band_of(out) == "student_linked"
    assert out["sentences"][0]["chains"][0]["ends"] == ["block"]


def test_l3b_confirmed_makes_traced_source():
    cfg = L1Config(l3b=True)
    out = run(LINKED, anchored_claim_events(), config=cfg,
              l3b=[L3bResult("s1", "k1", True)])
    assert band_of(out) == "traced_source"
    out = run(LINKED, anchored_claim_events(), config=cfg,
              l3b=[L3bResult("s1", "k1", False)])
    assert band_of(out) == "student_linked"


def test_l3b_added_blocks_trace():
    out = run(LINKED, anchored_claim_events(), config=L1Config(l3b=True),
              l3b=[L3bResult("s1", "k1", True, added=1)])
    s = out["sentences"][0]
    assert s["band"] == "student_linked" and s["added"] == 1


def test_l3b_suggestion_link_is_not_traced():
    d = doc(para(t("Typed words about the claim."), links=[link("k1", suggestion_id="g1")]))
    out = run(d, anchored_claim_events(), config=L1Config(l3b=True),
              l3b=[L3bResult("s1", "k1", True)])
    assert band_of(out) == "student_linked"


def test_l3b_needs_block_end_and_coach_end_gives_coach():
    ev_ = card_events(1, anchored=False) + [claim_ev(3)]
    out = run(LINKED, ev_, config=L1Config(l3b=True), l3b=[L3bResult("s1", "k1", True)])
    assert band_of(out) == "student_linked"
    ev_ = card_events(1, via="coach_answer", via_ref="q1", anchored=False) + [claim_ev(3)]
    out = run(LINKED, ev_, config=L1Config(l3b=True), l3b=[L3bResult("s1", "k1", True)])
    assert band_of(out) == "traced_coach"


def test_l3b_results_with_l3b_off_raise():
    with pytest.raises(ValueError):
        run(LINKED, anchored_claim_events(), l3b=[L3bResult("s1", "k1", True)])


# ---------------------------------------------------------------- D13
def test_d13_pasted_sentence_in_linked_paragraph():
    d = doc(para(t("z" * 30 + ".", "paste_ext", "p1"), t(" Typed sentence beside it."),
                 links=[link("k1")]))
    out = run(d, anchored_claim_events())
    a, b = out["sentences"]
    assert (a["band"], a["notes"]) == ("untraced", ["pasted_linked_not_checked"])
    assert (b["band"], b["notes"]) == ("student_linked", [])


@pytest.mark.parametrize("by,sug", [("student", None), ("student", "g1")])
def test_d13_boundary(by, sug):
    ln = [link("k1", by, sug)]
    d = doc(para(*fraction_sentence("paste_ext", 50, "p1"), links=ln))
    assert band_of(run(d, anchored_claim_events())) == "untraced"
    d = doc(para(*fraction_sentence("paste_ext", 49, "p1"), links=ln))
    assert band_of(run(d, anchored_claim_events())) == "student_linked"


def test_pasted_unlinked_has_no_note():
    d = doc(para(*fraction_sentence("paste_ext", 80, "p1")))
    s = run(d)["sentences"][0]
    assert s["band"] == "untraced" and s["notes"] == []


# ---------------------------------------------------------------- D-045
def test_honest_elaborating_writer():
    d = doc(para(t("First idea is this one. Then I elaborate further. And one more thought.",
                   "typed"), links=[link("k1")]))
    out = run(d, anchored_claim_events())
    assert all(s["mix"]["typed"] > 0 for s in out["sentences"])
    assert [s["band"] for s in out["sentences"]] == ["student_linked"] * 3
    assert out["bands"]["by_words"]["untraced"] == 0


def test_two_links_give_two_chains_and_two_units():
    d = doc(para(t("A thought about two claims."), links=[link("k1"), link("k2")]))
    ev_ = card_events(1) + [claim_ev(3), claim_ev(4, "k2", ("c1",))]
    out = run(d, ev_)
    assert [c["claim_id"] for c in out["sentences"][0]["chains"]] == ["k1", "k2"]
    assert [(c["id"], c["unit"]) for c in out["claims"]] == [("k1", "claim"), ("k2", "claim")]
    assert out["claims"][0]["sentence_ids"] == out["claims"][1]["sentence_ids"] == ["s1"]


# ---------------------------------------------------------------- forged marks
def test_forged_quote_unlinked():
    d = doc(para(t("Entirely different words appear here", "quote", "b1"), t(".")))
    out = run(d)
    s = out["sentences"][0]
    assert s["band"] == "untraced" and s["notes"] == ["label_not_confirmed"]
    assert s["mix"]["unconfirmed"] == 36 and s["mix"]["quote"] == 0
    assert s["marks"][0]["reason"] == "not_in_block" and s["quoted_words"] == 0


def test_forged_quote_majority_in_linked_paragraph_is_untraced():
    d = doc(para(t("Entirely different words appear here for sure", "quote", "b1"), t(" ok."),
                 links=[link("k1")]))
    out = run(d, anchored_claim_events())
    assert band_of(out) == "untraced"


def test_mark_without_run_result_is_unconfirmed():
    d = doc(para(t(QUOTE, "quote", "b1"), t(" tail.")))
    out = compute_l1(d, [], [])
    s = out["sentences"][0]
    assert s["mix"]["unconfirmed"] == len(QUOTE) and s["band"] == "untraced"


def test_hard_break_with_quote_mark_is_unconfirmed():
    d = doc(para(t("aa. "), {"type": "hard_break", "marks": [mk("quote", "b1")]}, t("bb.")))
    out = run(d)
    assert out["sentences"][0]["mix"]["unconfirmed"] == 0  # break sits between sentences
    assert len(out["sentences"]) == 2


# ---------------------------------------------------------------- chain breaks
def chain_of(d, events):
    return run(d, events)["sentences"][0]


def test_chain_no_link():
    s = chain_of(doc(para(t("Plain text."))), [])
    assert s["chains"] == [] and s["chain_break"] == "no_link"


def test_chain_breaks():
    d = doc(para(t("Plain text."), links=[link("k1")]))
    assert chain_of(d, [])["chains"][0]["break"] == "claim_not_found"
    assert chain_of(d, [])["chains"][0]["claim_kind"] == "missing"
    assert chain_of(d, [claim_ev(1, cards=())])["chains"][0]["break"] == "claim_has_no_cards"
    assert chain_of(d, [claim_ev(1)])["chains"][0]["break"] == "card_not_found"
    deleted = card_events(1) + [ev(3, "card.delete", card_id="c1"), claim_ev(4)]
    assert chain_of(d, deleted)["chains"][0]["break"] == "card_not_found"
    assert chain_of(d, card_events(1, anchored=False) + [claim_ev(3)])["chains"][0]["break"] \
        == "card_not_anchored"
    pasted = card_events(1, runs=[]) + [claim_ev(3)]
    c = chain_of(d, pasted)["chains"][0]
    assert c["break"] == "card_pasted" and c["cards"][0]["break"] == "card_pasted"


def test_coach_answer_card_ends_in_coach():
    d = doc(para(t("Plain text."), links=[link("k1")]))
    c = chain_of(d, card_events(1, via="coach_answer", via_ref="q1", anchored=False)
                 + [claim_ev(3)])["chains"][0]
    assert c["ends"] == ["coach"] and c["break"] is None


# ---------------------------------------------------------------- claim units
def test_unit_majority_by_words_and_tie_goes_later():
    # k1: three-word typed sentence (student_linked) vs two-word forged quote sentence
    d = doc(para(t("One two three. "), t("Four five", "quote", "b1"), t("."), links=[link("k1")]))
    out = run(d, anchored_claim_events())
    u = out["claims"][0]
    assert u["band"] == "student_linked" and u["words"] == 5
    # tie: 2 words student_linked vs 2 words untraced -> untraced (later)
    d = doc(para(t("One two. "), t("Four five", "quote", "b1"), t("."), links=[link("k1")]))
    out = run(d, anchored_claim_events())
    assert [s["band"] for s in out["sentences"]] == ["student_linked", "untraced"]
    assert out["claims"][0]["band"] == "untraced"


def test_unlinked_paragraph_unit_and_heading_counts_in_words():
    d = doc(heading(t("A title here")), para(t("Body text now.")), para())
    out = run(d)
    assert [(c["id"], c["unit"], c["claim_kind"]) for c in out["claims"]] == [("p2", "paragraph", None)]
    assert out["bands"]["total_words"] == 6
    assert out["sentences"][0]["band"] == "untraced"


def test_declared_unit():
    d = doc(para(t("Words."), links=[link("k1", "import")]))
    out = run(d, [ev(1, "claim.extracted", claim_id="k1", text="x", import_id="i1")])
    assert out["claims"][0]["band"] == "declared"
    assert out["bands"]["by_claims"]["declared"] == 1


# ---------------------------------------------------------------- proportions
def test_counts_and_sums():
    d = doc(para(t("Typed one two. "), t("Typed three."), links=[link("k1", suggestion_id="g1")]),
            para(t("Another paragraph here.")),
            para(t("Third."), links=[link("k1"), link("k2")]))
    ev_ = anchored_claim_events() + [ev(5, "map.suggestion", suggestion_id="g1"),
                                     ev(6, "map.suggestion", suggestion_id="g2")]
    out = run(d, ev_)
    b = out["bands"]
    assert b["inferred_links"] == 1 and b["map_suggestions"] == 2
    assert sum(b["by_words"].values()) == b["total_words"]
    assert sum(b["by_claims"].values()) == len(out["claims"]) == 3


# ---------------------------------------------------------------- L3b queue
def test_l3b_queue_reasons():
    cfg = L1Config(unlinked_untyped_pct=30)
    # 30 of 100 chars typed or pasted -> unlinked reason; 29 -> none (rest are unmarked)
    def unlinked(k):
        return doc(para({"type": "text", "text": "u" * (99 - k)}, t("b" * k, "typed"), t(".", "typed")))
    # unmarked chars first, then k typed chars, "." typed
    out = run(unlinked(29))  # typed = 29 + 1 = 30 -> reason
    assert out["l3b_queue"] == [{"sentence_id": "s1", "reasons": ["unlinked"]}]
    out = run(unlinked(28))  # typed = 29 -> none
    assert out["l3b_queue"] == []
    assert cfg.unlinked_untyped_pct == 30


def test_l3b_queue_student_link_and_pasted():
    d = doc(para(*fraction_sentence("paste_ext", 60, "p1"), links=[link("k1")]),
            para(t("x" * 10 + ".", "quote", "b1"), links=[link("k1", "coach")]))
    out = run(d, anchored_claim_events())
    assert out["l3b_queue"] == [{"sentence_id": "s1", "reasons": ["pasted", "student_link"]}]


# ---------------------------------------------------------------- seal, positions, determinism
def test_post_seal_events_do_not_change_output():
    d = doc(para(t("Typed words about the claim."), links=[link("k1")]))
    base = anchored_claim_events()
    after = base + [ev(10, "claim.edit", claim_id="k1", text="y", card_ids=[], parent_claim_id=None),
                    ev(11, "map.suggestion", suggestion_id="g1"),
                    ev(12, "card.delete", card_id="c1")]
    a = run(d, base, seal_seq=4)
    b = run(d, after, seal_seq=4)
    assert canonical_json(a) == canonical_json(b)
    assert run(d, after)["sentences"][0]["chain_break"] is None
    assert run(d, after)["sentences"][0]["chains"][0]["break"] == "claim_has_no_cards"


def test_positions_utf16_after_emoji():
    d = doc(para(t("😀 Hi there. Second one.")))
    out = run(d)
    s1, s2 = out["sentences"]
    assert s1["from"] == 1 and s1["to"] == 1 + 2 + 10  # emoji takes two positions
    assert s2["from"] == 14 and s2["to"] == 14 + len("Second one.")
    assert out["paragraphs"][0]["from"] == 1


def test_no_sentence_text_and_paragraph_ids():
    d = doc(para(t("Secret words here.")), {"type": "blockquote", "content": [para(t("Quoted."))]})
    out = run(d)
    assert "Secret" not in canonical_json(out).decode()
    assert [p["id"] for p in out["paragraphs"]] == ["p1", "p2"]


def test_determinism_and_no_floats():
    d = doc(para(t("Typed words. "), t(QUOTE, "quote", "b1"), t(" end."), links=[link("k1")]),
            para(t("More text here.")))
    ev_ = anchored_claim_events() + [ev(5, "map.suggestion", suggestion_id="g1")]
    a = run(d, ev_)
    b = run(d, list(ev_))
    c = run(d, list(reversed(ev_)))
    assert canonical_json(a) == canonical_json(b) == canonical_json(c)

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                assert isinstance(k, str)
                walk(v)
        elif isinstance(x, (list, tuple)):
            for v in x:
                walk(v)
        else:
            assert not isinstance(x, float)
    walk(a)
    assert list(a["sentences"][0]["mix"]) == sorted(a["sentences"][0]["mix"])


def test_config_validation_and_json():
    for kw in ({"paste_ext_pct": 101}, {"paste_ext_pct": True}, {"declared_import_pct": -1},
               {"unlinked_untyped_pct": 1.5}, {"min_quote_words": 0}):
        with pytest.raises(ValueError):
            L1Config(**kw)
    assert L1Config().to_json() == {
        "flags": {"l3b": False},
        "thresholds": {"declared_import_pct": 50, "min_quote_words": 4, "paste_ext_pct": 50,
                       "unlinked_untyped_pct": 30}}


# ---------------------------------------------------------------- end to end
def test_end_to_end_compile_then_l1():
    from app.events_service import EventService
    from tests.test_replay_compile import Clock, Writer
    clock = Clock()
    w = Writer(EventService(":memory:", clock), clock)
    w.insert("My own sentence. ")
    w.insert("Teachers decide what to ask", "quote", "b1")
    w.insert(" fine.")
    w.checkpoint()
    w.submit()
    s = InMemorySources(blocks={"b1": "Teachers decide what to ask next about the work"})
    res = compile_marks(w.events(), w.loader(), s)
    out = l1_from_compile(res, w.events())
    assert out["status"] == "complete" and out["built_from"] == "replay"
    assert [x["band"] for x in out["sentences"]] == ["untraced", "traced_source"]
    again = l1_from_compile(res, list(reversed(w.events())))
    assert canonical_json(out) == canonical_json(again)


def test_card_edit_does_not_revive_deleted_card():
    d = doc(para(t("Plain text."), links=[link("k1")]))
    evs = card_events(1) + [ev(3, "card.delete", card_id="c1"),
                            ev(4, "card.edit", card_id="c1", text="edited",
                               origin_runs=typed_runs("edited")), claim_ev(5)]
    assert run(d, evs)["sentences"][0]["chains"][0]["break"] == "card_not_found"
    evs = [ev(1, "card.edit", card_id="c1", text="new", origin_runs=typed_runs("new")),
           ev(2, "card.anchor", card_id="c1", source_id="s1", block_id="b1"), claim_ev(3)]
    assert run(d, evs)["sentences"][0]["chains"][0]["ends"] == ["block"]


def test_card_edit_without_via_keeps_previous_via():
    d = doc(para(t("Plain text."), links=[link("k1")]))
    evs = card_events(1, via="coach_answer", via_ref="q1", anchored=False) + [
        ev(3, "card.edit", card_id="c1", text="reworded", origin_runs=typed_runs("reworded")),
        claim_ev(4)]
    assert run(d, evs)["sentences"][0]["chains"][0]["ends"] == ["coach"]
