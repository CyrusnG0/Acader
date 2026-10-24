"""Mark check: each origin run must point at text that really exists in its source."""
import json

from prosemirror.model import Node
from prosemirror.transform import Transform

from engine.events import canonical_json
from engine.provenance import (InMemorySources, check_marks, coach_answer_from_runs,
                               normalise, origin_runs, word_count)
from engine.replay import EMPTY_DOC, load_schema


def mk(kind, ref=None):
    return {"type": "origin", "attrs": {"kind": kind, "ref": ref}}


def t(text, kind=None, ref=None, *extra):
    marks = ([mk(kind, ref)] if kind else []) + [{"type": m} for m in extra]
    node = {"type": "text", "text": text}
    if marks:
        node["marks"] = marks
    return node


def br(kind=None, ref=None):
    node = {"type": "hard_break"}
    if kind:
        node["marks"] = [mk(kind, ref)]
    return node


def para(*inline):
    return {"type": "paragraph", "attrs": {"links": []}, "content": list(inline)}


def doc(*paras):
    return {"type": "doc", "content": list(paras)}


BLOCK = "The quick brown fox jumps over the lazy dog"


def one(d, sources):
    res = check_marks(d, sources)
    assert len(res) == 1
    return res[0]


def src(**kw):
    return InMemorySources(**kw)


# 1
def test_forged_quote_not_in_block():
    s = src(blocks={"b1": BLOCK})
    r = one(doc(para(t("Entirely different words appear here", "quote", "b1"))), s)
    assert (r.reason, r.confirmed) == ("not_in_block", False)


def test_quote_checks_only_its_own_block():
    s = src(blocks={"b1": BLOCK, "b2": "Something else entirely different from the first"})
    r = one(doc(para(t("Something else entirely different", "quote", "b1"))), s)
    assert (r.reason, r.confirmed) == ("not_in_block", False)


# 2
def test_quote_word_minimum():
    s = src(blocks={"b1": BLOCK})
    r3 = one(doc(para(t("quick brown fox", "quote", "b1"))), s)
    assert (r3.reason, r3.confirmed) == ("too_short", False)
    r4 = one(doc(para(t("quick brown fox jumps", "quote", "b1"))), s)
    assert (r4.reason, r4.confirmed) == ("ok", True)


# 3
def test_whole_block_exception():
    s = src(blocks={"b1": "Two words"})
    r = one(doc(para(t("Two words", "quote", "b1"))), s)
    assert (r.reason, r.confirmed) == ("ok", True)


def test_whole_block_with_different_whitespace_and_quotes():
    s = src(blocks={"b1": "“He said” it’s"})
    r = one(doc(para(t('"He   said" it\'s', "quote", "b1"))), s)
    assert (r.reason, r.confirmed) == ("ok", True)


# 4
def _answer():
    text = "Pasted opening. My own typed thought."
    cut = len("Pasted opening. ")
    return text, coach_answer_from_runs(text, [
        {"from": 0, "to": cut, "kind": "paste_ext"},
        {"from": cut, "to": len(text), "kind": "typed"}])


def test_coach_pasted_part_and_spanning_part():
    _, a = _answer()
    s = src(coach={"q1": a})
    r = one(doc(para(t("Pasted opening.", "coach", "q1"))), s)
    assert (r.reason, r.confirmed) == ("pasted_in_answer", False)
    r = one(doc(para(t("opening. My own typed", "coach", "q1"))), s)
    assert (r.reason, r.confirmed) == ("pasted_in_answer", False)


def test_coach_typed_part_ok_and_unknown_text():
    _, a = _answer()
    s = src(coach={"q1": a})
    r = one(doc(para(t("My own typed thought.", "coach", "q1"))), s)
    assert (r.reason, r.confirmed) == ("ok", True)
    r = one(doc(para(t("Not in the answer", "coach", "q1"))), s)
    assert (r.reason, r.confirmed) == ("not_in_answer", False)


# 5
def test_coach_typed_part_not_at_offset_zero():
    _, a = _answer()
    assert a.typed_ranges[0][0] > 0
    r = one(doc(para(t("typed thought", "coach", "q1"))), src(coach={"q1": a}))
    assert r.reason == "ok"


def test_coach_text_moved_to_another_paragraph_via_transform():
    schema = load_schema()
    start = doc(para(t("My own typed thought.", "coach", "q1")), para())
    d0 = Node.from_json(schema, start)
    tr = Transform(d0)
    mark = schema.marks["origin"].create({"kind": "coach", "ref": "q1"})
    tr.delete(1, 1 + len("My own typed thought."))
    second = 3  # start of the second paragraph's content: 2 (empty para1) + 1
    tr.insert(second, schema.text("My own typed thought.", [mark]))
    moved = tr.doc
    runs = origin_runs(moved)
    assert [r.text for r in runs] == ["My own typed thought."]
    assert runs[0].from_ == second
    _, a = _answer()
    res = check_marks(moved, src(coach={"q1": a}))
    assert [(c.reason, c.confirmed) for c in res] == [("ok", True)]


# 6
def test_coach_gap_counts_as_pasted():
    text = "aaaa bbbb cccc dddd"
    a = coach_answer_from_runs(text, [{"from": 0, "to": 4, "kind": "typed"},
                                      {"from": 10, "to": 19, "kind": "typed"}])
    assert a.typed_ranges == ((0, 4), (10, 19))
    r = one(doc(para(t("bbbb", "coach", "q1"))), src(coach={"q1": a}))
    assert (r.reason, r.confirmed) == ("pasted_in_answer", False)


def test_coach_runs_clamped_merged_and_empty_dropped():
    a = coach_answer_from_runs("abcdef", [
        {"from": 4, "to": 99, "kind": "typed"}, {"from": 0, "to": 3, "kind": "typed"},
        {"from": 2, "to": 4, "kind": "typed"}, {"from": 5, "to": 5, "kind": "typed"},
        {"from": -5, "to": 0, "kind": "typed"}, {"from": 0, "to": 6, "kind": "paste_ext"}])
    assert a.typed_ranges == ((0, 6),)


# 7
def test_import_and_helper_pass_and_fail():
    s = src(imports={"i1": "alpha  beta gamma"}, helper={"h1": "delta epsilon"})
    r = one(doc(para(t("alpha beta", "import", "i1"))), s)
    assert (r.reason, r.confirmed) == ("ok", True)
    r = one(doc(para(t("alpha zeta", "import", "i1"))), s)
    assert (r.reason, r.confirmed) == ("not_in_import", False)
    r = one(doc(para(t("delta epsilon", "helper", "h1"))), s)
    assert (r.reason, r.confirmed) == ("ok", True)
    r = one(doc(para(t("delta zeta", "helper", "h1"))), s)
    assert (r.reason, r.confirmed) == ("not_in_output", False)


def test_missing_ref_and_origin_not_found():
    s = src()
    for kind in ("quote", "coach", "import", "helper"):
        r = one(doc(para(t("some text here now", kind, None))), s)
        assert (r.reason, r.confirmed) == ("missing_ref", False)
        r = one(doc(para(t("some text here now", kind, ""))), s)
        assert r.reason == "missing_ref"
        r = one(doc(para(t("some text here now", kind, "nope"))), s)
        assert (r.reason, r.confirmed) == ("origin_not_found", False)


# 8
def test_run_split_by_bold_is_one_run():
    s = src(blocks={"b1": BLOCK})
    d = doc(para(t("The quick ", "quote", "b1"), t("brown", "quote", "b1", "strong"),
                 t(" fox jumps", "quote", "b1", "em")))
    res = check_marks(d, s)
    assert len(res) == 1
    assert (res[0].reason, res[0].confirmed) == ("ok", True)
    assert res[0].from_ == 1 and res[0].to == 1 + len("The quick brown fox jumps")


def test_same_block_quoted_twice_gives_two_runs():
    s = src(blocks={"b1": BLOCK})
    d = doc(para(t("The quick brown fox jumps over", "quote", "b1"), t(" and then I argue "),
                 t("lazy dog", "quote", "b1")))
    res = check_marks(d, s)
    assert [(r.reason, r.confirmed) for r in res] == [("ok", True), ("too_short", False)]


# 9
def test_normalisation_in_checks():
    s = src(blocks={"b1": "She said \"yes\" and it’s fine today"})
    r = one(doc(para(t("said “yes” and it's fine", "quote", "b1"))), s)
    assert r.reason == "ok"
    s = src(blocks={"b1": "She said “yes” and it’s fine today"})
    r = one(doc(para(t("said \"yes\" and it's fine", "quote", "b1"))), s)
    assert r.reason == "ok"


def test_nbsp_double_spaces_and_hard_break():
    s = src(blocks={"b1": "one two three four five"})
    d = doc(para(t("one  two", "quote", "b1"), br("quote", "b1"),
                 t("three four", "quote", "b1")))
    res = check_marks(d, s)
    assert len(res) == 1
    assert res[0].reason == "ok"


def test_normalise_unit():
    assert normalise("‘a’ ‚b‛ ′c` ´") == "'a' 'b' 'c' '"
    assert normalise("“x” „y‟ ″z″ «q»") == '"x" "y" "z" "q"'
    assert normalise("  a \t\n b  c d  ") == "a b c d"
    assert normalise("Case") == "Case"
    assert normalise("ﬁ") == "ﬁ"  # no NFKC
    assert word_count("") == 0 and word_count("a b  c") == 3


# 10
def test_typed_and_paste_ext_not_checked_and_no_origin_ignored():
    d = doc(para(t("typed words", "typed"), t("pasted words", "paste_ext", "p1"),
                 t("plain words")))
    assert check_marks(d, src()) == []
    kinds = [r.kind for r in origin_runs(d)]
    assert kinds == ["typed", "paste_ext", "none"]


def test_runs_never_cross_paragraphs():
    s = src(blocks={"b1": BLOCK})
    d = doc(para(t("The quick brown fox", "quote", "b1")),
            para(t("jumps over the lazy", "quote", "b1")))
    res = check_marks(d, s)
    assert len(res) == 2 and all(r.confirmed for r in res)


def test_unmarked_hard_break_ends_run():
    d = doc(para(t("one two", "quote", "b1"), br(), t("three four", "quote", "b1")))
    assert len(origin_runs(d)) == 2


def test_runs_in_nested_blocks_and_headings():
    d = doc({"type": "heading", "attrs": {"level": 1}, "content": [t("Head", "typed")]},
            {"type": "blockquote", "content": [para(t("inner words here ok", "quote", "b1"))]})
    runs = origin_runs(d)
    assert [r.text for r in runs] == ["Head", "inner words here ok"]
    assert runs[0].from_ == 1 and runs[0].to == 5


# 11
def test_to_json_shape_and_determinism():
    s = src(blocks={"b1": BLOCK})
    d = doc(para(t("quick brown fox jumps", "quote", "b1"), t(" x "), t("zzz", "quote", "b1")))
    a = [r.to_json() for r in check_marks(d, s)]
    b = [r.to_json() for r in check_marks(d, s)]
    assert all(set(x) == {"from", "to", "kind", "ref", "confirmed", "reason"} for x in a)
    assert canonical_json(a) == canonical_json(b)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_accepts_node_and_empty_doc():
    assert check_marks(Node.from_json(load_schema(), EMPTY_DOC), src()) == []
