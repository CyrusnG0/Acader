"""L1 receipt facts (provenance.md section 7)."""
import re

from engine.events import canonical_json
from engine.provenance import InMemorySources, build_trail, check_marks, compute_facts, compute_l1

T = "2026-11-02T14:00:00Z"
KINDS = {"b1": "limitation", "b2": "results", "b3": "weird"}


def ev(seq, type_, **payload):
    return {"seq": seq, "type": type_, "payload": payload, "ts": T}


def mk(kind, ref=None):
    return {"type": "origin", "attrs": {"kind": kind, "ref": ref}}


def t(text, kind=None, ref=None):
    node = {"type": "text", "text": text}
    if kind:
        node["marks"] = [mk(kind, ref)]
    return node


EMPTY = {"type": "doc", "content": [{"type": "paragraph", "attrs": {"links": []}, "content": []}]}


def facts(events, doc=EMPTY, **kw):
    evs = list(events)
    return compute_facts(evs, doc, build_trail(evs), block_kinds=KINDS, **kw)


def one_para(*inline):
    return {"type": "doc", "content": [{"type": "paragraph", "attrs": {"links": []},
                                        "content": list(inline)}]}


def card(seq, cid="c1", text="abc", runs=True):
    return ev(seq, "card.create", card_id=cid, text=text,
              origin_runs=[{"from": 0, "to": len(text), "kind": "typed"}] if runs else [],
              via="typed")


# ---------------------------------------------------------------- reading
def test_reading_opened_and_anchored_by_kind():
    evs = [ev(1, "source.add", source_id="s2", origin="door"),
           ev(2, "source.add", source_id="s1", origin="teacher"),
           ev(3, "source.view_span", source_id="s1", block_ids=["b1", "b2"]),
           ev(4, "aid.pin_opened", source_id="s1", block_id="b3", pin_kind="limitation"),
           ev(5, "aid.pin_opened", source_id="s1", block_id="b1", pin_kind="limitation"),
           card(6), ev(7, "card.anchor", card_id="c1", source_id="s1", block_id="b2"),
           card(8, "c2"), ev(9, "card.anchor", card_id="c2", source_id="s1", block_id="b1"),
           ev(10, "card.delete", card_id="c2")]
    r = facts(evs)["reading"]
    assert [x["source_id"] for x in r] == ["s1", "s2"]
    assert r[0]["opened"] == {"limitation": 1, "other": 1, "results": 1}
    assert r[0]["anchored"] == {"results": 1}  # the deleted card's anchor is not counted
    assert r[0]["event_ids"] == [2, 3, 4, 5, 7, 9]
    assert r[1]["opened"] == {} and r[1]["event_ids"] == [1]


# ---------------------------------------------------------------- moments
def _limit_base(pin_seq=3, edit_seq=6, pin_source="s1"):
    return [card(1), ev(2, "card.anchor", card_id="c1", source_id="s1", block_id="b2"),
            ev(pin_seq, "aid.pin_opened", source_id=pin_source, block_id="b1",
               pin_kind="limitation"),
            ev(edit_seq, "claim.edit", claim_id="k1", text="x", card_ids=["c1"],
               parent_claim_id=None)]


def test_moment_claim_edit_after_limitation_positive():
    m = facts(_limit_base())["moments"]
    assert m == [{"kind": "claim_edit_after_limitation", "seq": 6, "ts": T, "claim_id": "k1",
                  "source_id": "s1", "pin_seq": 3}]


def test_moment_negative_pin_after_edit_or_other_source():
    assert facts(_limit_base(pin_seq=7, edit_seq=6))["moments"] == []
    assert facts(_limit_base(pin_source="s9"))["moments"] == []
    other = [e for e in _limit_base() if e["type"] != "card.anchor"]
    assert facts(other)["moments"] == []
    notlim = _limit_base()
    notlim[2]["payload"]["pin_kind"] = "results"
    assert facts(notlim)["moments"] == []


def test_moment_latest_pin_and_smallest_source():
    evs = [card(1), ev(2, "card.anchor", card_id="c1", source_id="s1", block_id="b2"),
           ev(3, "card.anchor", card_id="c1", source_id="s0", block_id="b2"),
           ev(4, "aid.pin_opened", source_id="s1", block_id="b1", pin_kind="limitation"),
           ev(5, "aid.pin_opened", source_id="s1", block_id="b1", pin_kind="limitation"),
           ev(6, "aid.pin_opened", source_id="s0", block_id="b1", pin_kind="limitation"),
           ev(7, "claim.edit", claim_id="k1", text="x", card_ids=["c1"], parent_claim_id=None)]
    m = facts(evs)["moments"][0]
    assert (m["source_id"], m["pin_seq"]) == ("s0", 6)


def test_moment_set_aside_needs_reason_tag_and_omits_note():
    evs = [ev(1, "card.set_aside", source_id="s1", reason_tag="off_topic", note="private words"),
           ev(2, "card.set_aside", source_id="s1", reason_tag="", note="x"),
           ev(3, "card.set_aside", source_id="s1", note="y")]
    m = facts(evs)["moments"]
    assert m == [{"kind": "set_aside", "seq": 1, "ts": T, "source_id": "s1",
                  "reason_tag": "off_topic"}]
    assert "private" not in canonical_json(m).decode()


def test_moments_coach_disagreed_and_revised():
    evs = [ev(1, "coach.outcome", q_id="q1", outcome="disagreed", answer_text="because", origin_runs=[]),
           ev(2, "coach.outcome", q_id="q2", outcome="disagreed", answer_text="  ", origin_runs=[]),
           ev(3, "coach.outcome", q_id="q3", outcome="revised", answer_text="", origin_runs=[]),
           ev(4, "coach.outcome", q_id="q4", outcome="answered", answer_text="a", origin_runs=[])]
    m = facts(evs)["moments"]
    assert [(x["kind"], x["q_id"]) for x in m] == [("coach_disagreed", "q1"),
                                                   ("coach_revised", "q3")]


# ---------------------------------------------------------------- coach
def test_coach_counts_latest_outcome_wins():
    evs = [ev(1, "coach.ask", q_id="q1", case="B", pillar="logic"),
           ev(2, "coach.ask", q_id="q2", case="C", pillar="reading"),
           ev(3, "coach.ask", q_id="q3", case="C", pillar="writing"),
           ev(4, "coach.outcome", q_id="q1", outcome="declined", answer_text="", origin_runs=[]),
           ev(5, "coach.outcome", q_id="q1", outcome="answered", answer_text="a", origin_runs=[]),
           ev(6, "coach.outcome", q_id="q2", outcome="revised", answer_text="", origin_runs=[])]
    c = facts(evs)["coach"]
    assert c["asked"] == 3 and c["by_case"] == {"B": 1, "C": 2}
    assert c["by_pillar"] == {"communication": 0, "logic": 1, "reading": 1, "writing": 1}
    assert c["by_outcome"] == {"answered": 1, "declined": 0, "disagreed": 0, "no_outcome": 1,
                               "revised": 1}
    assert [(q["q_id"], q["outcome"], q["outcome_seq"]) for q in c["questions"]] == [
        ("q1", "answered", 5), ("q2", "revised", 6), ("q3", "no_outcome", None)]


# ---------------------------------------------------------------- pastes
def test_paste_survival_after_part_deleted():
    d = one_para(t("x" * 6, "paste_ext", "p1"), t(" typed ", "typed"), t("y" * 3, "paste_ext", "p2"))
    evs = [ev(1, "editor.paste", paste_id="p1", size_chars=10, kind="external"),
           ev(2, "editor.paste", paste_id="p2", size_chars=3, kind="external"),
           ev(3, "editor.paste", paste_id="p3", size_chars=99, kind="internal")]
    p = facts(evs, d)["pastes"]
    assert p["editor"]["count"] == 2 and p["editor"]["chars"] == 13
    assert p["editor"]["surviving_chars"] == 9
    assert p["editor"]["items"][0] == {"paste_id": "p1", "seq": 1, "size_chars": 10,
                                       "surviving_chars": 6}
    assert p["final_paste_ext_chars"] == 9


def test_paste_cards_and_coach_answers():
    evs = [card(1, "c1", "typed text"), card(2, "c2", "pasted!!!", runs=False),
           ev(3, "card.create", card_id="c3", text="half", via="typed",
              origin_runs=[{"from": 0, "to": 2, "kind": "typed"}]),
           ev(4, "card.delete", card_id="c3"),
           ev(5, "coach.outcome", q_id="q1", outcome="answered", answer_text="abcdef",
              origin_runs=[{"from": 0, "to": 2, "kind": "typed"}]),
           ev(6, "coach.outcome", q_id="q1", outcome="revised", answer_text="abcdef",
              origin_runs=[{"from": 0, "to": 4, "kind": "typed"}]),
           ev(7, "coach.outcome", q_id="q2", outcome="answered", answer_text="all typed",
              origin_runs=[{"from": 0, "to": 9, "kind": "typed"}])]
    p = facts(evs)["pastes"]
    assert p["cards"] == {"cards_with_paste": 1, "chars": 9}
    assert p["coach_answers"] == {"answers_with_paste": 1, "chars": 2}  # latest outcome only


def test_replacement_edits_sum():
    evs = [ev(1, "editor.batch", input_kind={"keyboard": 5, "replacement": 2}),
           ev(2, "editor.batch", input_kind={"keyboard": 1}),
           ev(3, "editor.batch", input_kind={"replacement": 3})]
    assert facts(evs)["replacement_edits"] == {"count": 5, "lower_bound": True,
                                               "event_ids": [1, 3]}


# ---------------------------------------------------------------- declared and unanchored
def test_declared_imports_by_tool_without_text():
    evs = [ev(1, "import.declared", import_id="i1", tool_name="ToolA", size_chars=100,
              raw_text_ref="secret-ref"),
           ev(2, "import.declared", import_id="i2", tool_name="ToolA", size_chars=50),
           ev(3, "import.declared", import_id="i3", tool_name="ToolB", size_chars=7),
           ev(4, "claim.extracted", claim_id="k1", text="a declared claim", import_id="i1"),
           ev(5, "claim.extracted", claim_id="k2", text="another", import_id="i2"),
           card(6), ev(7, "card.anchor", card_id="c1", source_id="s1", block_id="b2"),
           ev(8, "claim.edit", claim_id="k2", text="another", card_ids=["c1"],
              parent_claim_id=None)]
    d = facts(evs)["declared"]
    assert [i["import_id"] for i in d["imports"]] == ["i1", "i2", "i3"]
    assert d["by_tool"] == {"ToolA": {"count": 2, "size_chars": 150},
                            "ToolB": {"count": 1, "size_chars": 7}}
    assert d["declared_claims"] == 2 and d["declared_claims_anchored"] == 1
    out = canonical_json(facts(evs)).decode()
    assert "secret-ref" not in out and "a declared claim" not in out


def test_unanchored_claims():
    evs = [card(1), ev(2, "card.delete", card_id="c1"),
           card(3, "c2"),
           ev(4, "claim.create", claim_id="kb", text="x", card_ids=["c1"], parent_claim_id=None),
           ev(5, "claim.create", claim_id="ka", text="x", card_ids=[], parent_claim_id=None),
           ev(6, "claim.create", claim_id="kc", text="x", card_ids=["c2"], parent_claim_id=None),
           ev(7, "claim.extracted", claim_id="kd", text="x", import_id="i1")]
    u = facts(evs)["unanchored_claims"]
    assert u["count"] == 2 and u["claim_ids"] == ["ka", "kb"]


# ---------------------------------------------------------------- guard rails
def test_no_forbidden_keys():
    evs = [ev(1, "coach.ask", q_id="q1", case="B", pillar="logic"),
           ev(2, "coach.outcome", q_id="q1", outcome="answered", answer_text="a", origin_runs=[]),
           ev(3, "import.declared", import_id="i1", tool_name="ToolA", size_chars=1),
           ev(4, "source.add", source_id="s1")]
    bad = re.compile(r"order|first|ratio|resolved|grade|score")
    keys = []

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                keys.append(k)
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(facts(evs))
    assert keys and not [k for k in keys if bad.search(k)]


def test_facts_inside_l1_output_and_floats_free():
    d = one_para(t("Typed words here."))
    evs = [ev(1, "source.add", source_id="s1")]
    out = compute_l1(d, check_marks(d, InMemorySources()), evs, block_kinds=KINDS)
    assert out["facts"]["reading"][0]["source_id"] == "s1"
    canonical_json(out)


def test_import_without_tool_name_is_unknown():
    evs = [ev(1, "import.declared", import_id="i1", size_chars=5),
           ev(2, "import.declared", import_id="i2", tool_name=None, size_chars=6),
           ev(3, "import.declared", import_id="i3", tool_name=7, size_chars=1)]
    d = facts(evs)["declared"]
    assert d["by_tool"] == {"unknown": {"count": 3, "size_chars": 12}}
    canonical_json(d)
