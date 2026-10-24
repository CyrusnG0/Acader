"""Spike S1 + T-011: Python replay parity (evaluation.md §1, event-log.md §5, D6, D33, D-044).

The fixture is written by the browser editor test (web/src/editor/s1.test.ts):
each case holds the start doc, the steps TipTap recorded, the browser's final
doc and its doc_hash. prosemirror-py, loading the same web/schema.json, must
replay the steps to the same doc, the same marks, the same paragraph links and
the same hash.
"""
import copy
import json
from pathlib import Path

import pytest

from engine.replay import ALLOWED_STEP_TYPES, ReplayError, doc_hash, load_schema, replay_steps

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "replay" / "s1_steps.json"
SCHEMA_JSON = Path(__file__).resolve().parents[2] / "web" / "schema.json"
DATA = json.loads(FIXTURE.read_text(encoding="utf-8"))
CASES = DATA["cases"]
IDS = [c["name"] for c in CASES]

# The cases the spike must cover (evaluation.md §1) and the link and node cases
# of T-011. Dropping one from the editor test makes this list fail.
REQUIRED = {
    "typed_plain", "typed_inside_quote", "typed_inside_paste_ext", "typed_inside_helper",
    "typed_inside_coach", "typed_inside_import", "typed_edges_quote", "typed_between_spans",
    "select_all_type", "typed_astral", "split_paragraph", "delete_across_edge",
    "replacement_in_quote", "ime_in_quote", "dom_edit_in_quote", "paste_external_html",
    "paste_external_in_quote", "copy_paste_internal", "cut_paste_move", "paste_other_log",
    "paste_malformed_slice", "drag_move_internal", "drop_external", "undo_redo",
    "keystroke_handle_text_input",
    # T-011
    "link_command", "unlink_command", "accept_suggestion",
    "typed_inside_linked", "typed_edges_linked", "sentence_added_linked", "ime_in_linked",
    "replacement_in_linked", "delete_all_text_linked",
    "split_linked_middle", "enter_end_linked", "enter_start_linked",
    "join_backspace_union", "join_delete_forward", "join_across_three",
    "paste_internal_paragraphs", "paste_internal_fragment", "paste_internal_into_empty",
    "paste_external_into_linked", "paste_external_multi_para",
    "undo_redo_join", "undo_redo_link",
    "heading_levels", "paragraph_to_heading_drops_links", "bullet_list_items", "ordered_list",
    "blockquote_wrap_linked", "hard_break", "bold_italic",
}

NODES = ["doc", "paragraph", "heading", "blockquote", "bullet_list", "ordered_list",
         "list_item", "text", "hard_break"]


def case(name):
    return next(c for c in CASES if c["name"] == name)


def textblocks(node):
    """Textblocks (paragraph, heading) in document order, from doc JSON."""
    if node["type"] in ("paragraph", "heading"):
        yield node
        return
    for child in node.get("content", []):
        yield from textblocks(child)


def runs(doc_json):
    """[(text, origin kind, ref)] per textblock, in document order."""
    out = []
    for block in textblocks(doc_json):
        row = []
        for t in block.get("content", []):
            if t["type"] != "text":
                continue
            marks = {m["type"]: m.get("attrs", {}) for m in t.get("marks", [])}
            o = marks.get("origin")
            row.append((t["text"], o and o["kind"], o and o.get("ref")))
        out.append(row)
    return out


def links(doc_json):
    """Per paragraph, in document order: ['c1/student', 'c2/coach', 'c1/student/s1']."""
    return [
        [f'{l["claim_id"]}/{l["by"]}' + (f'/{l["suggestion_id"]}' if "suggestion_id" in l else "")
         for l in p.get("attrs", {}).get("links", [])]
        for p in textblocks(doc_json) if p["type"] == "paragraph"
    ]


def replayed(name):
    c = case(name)
    return replay_steps(c["start"], c["steps"]).to_json()


def test_fixture_covers_every_s1_case():
    assert REQUIRED <= set(IDS)
    assert DATA["schema_version"] == json.loads(SCHEMA_JSON.read_text())["x-writing-room"]["schema_version"]


@pytest.mark.parametrize("c", CASES, ids=IDS)
def test_python_replay_matches_browser(c):
    doc = replay_steps(c["start"], c["steps"])
    assert doc.to_json() == c["doc"]
    assert doc_hash(doc) == c["doc_hash"]


@pytest.mark.parametrize("c", CASES, ids=IDS)
def test_every_character_has_exactly_one_origin(c):
    for block in textblocks(c["doc"]):
        for t in block.get("content", []):
            if t["type"] == "text":
                assert [m["type"] for m in t.get("marks", [])].count("origin") == 1, t


@pytest.mark.parametrize("c", CASES, ids=IDS)
def test_every_fixture_step_type_is_allowed(c):
    assert {s["stepType"] for s in c["steps"]} <= ALLOWED_STEP_TYPES


def test_fixture_exercises_attr_and_replace_around_steps():
    types = {s["stepType"] for c in CASES for s in c["steps"]}
    assert {"attr", "replaceAround", "replace", "addMark"} <= types


def test_typed_inside_a_linked_paragraph_is_typed_and_links_are_unchanged():
    doc = replayed("typed_inside_linked")
    assert runs(doc) == [[("abc", "quote", "b81"), ("XY", "typed", None), ("def", "quote", "b81")]]
    assert links(doc) == [["c1/student"]]


def test_a_join_replays_to_the_union_in_order():
    doc = replayed("join_backspace_union")
    assert links(doc) == [["c1/student", "c2/coach"]]
    assert links(replayed("join_delete_forward")) == [["c1/student", "c2/coach"]]
    assert links(replayed("join_across_three")) == [["c1/student", "c3/student"]]


def test_enter_at_the_end_gives_a_paragraph_with_no_links():
    assert links(replayed("enter_end_linked")) == [["c1/student"], []]
    assert links(replayed("enter_start_linked")) == [[], ["c1/student"]]


def test_accepted_suggestion_keeps_its_suggestion_id():
    assert links(replayed("accept_suggestion")) == [["c1/student/s1", "c1/student"]]


def test_external_paste_brings_no_link():
    assert links(replayed("paste_external_into_linked")) == [["c1/student"]]
    assert links(replayed("paste_external_multi_para")) == [["c1/student"], [], ["c1/student"]]


def test_external_paste_is_paste_ext_in_the_replayed_doc():
    doc = replayed("paste_external_html")
    assert runs(doc) == [[("x", "typed", None), ("outside forged bold", "paste_ext", "log_A_paste_1")]]


def test_astral_positions_match():
    doc = replayed("typed_astral")
    assert [r[0] for r in runs(doc)[0]] == ["café 😀", "🎓!", " naïve"]


def test_a_changed_step_breaks_parity():
    c = copy.deepcopy(case("typed_inside_quote"))
    add = next(s for s in c["steps"] if s["stepType"] == "addMark")
    add["mark"]["attrs"]["kind"] = "quote"
    add["mark"]["attrs"]["ref"] = "b81"
    doc = replay_steps(c["start"], c["steps"])
    assert doc.to_json() != c["doc"]
    assert doc_hash(doc) != c["doc_hash"]


def test_dropping_a_step_breaks_parity():
    c = copy.deepcopy(case("undo_redo"))
    last_replace = max(i for i, s in enumerate(c["steps"]) if s["stepType"] == "replace")
    del c["steps"][last_replace]
    doc = replay_steps(c["start"], c["steps"])
    assert doc_hash(doc) != c["doc_hash"]


def test_changing_an_attr_step_breaks_parity():
    c = copy.deepcopy(case("link_command"))
    attr = next(s for s in c["steps"] if s["stepType"] == "attr")
    attr["value"] = [{"claim_id": "c7", "by": "student"}]
    assert doc_hash(replay_steps(c["start"], c["steps"])) != c["doc_hash"]


def test_a_kind_outside_the_closed_list_is_refused():
    c = copy.deepcopy(case("typed_plain"))
    add = next(s for s in c["steps"] if s["stepType"] == "addMark")
    add["mark"]["attrs"]["kind"] = "ai"
    with pytest.raises(ReplayError):
        replay_steps(c["start"], c["steps"])


# ---- the links validator (D-044) ----

def _para(links_value):
    return {"type": "doc", "content": [{"type": "paragraph", "attrs": {"links": links_value}}]}


def _attr_step(links_value):
    return {"stepType": "attr", "pos": 0, "attr": "links", "value": links_value}


GOOD_LINKS = [
    [],
    [{"claim_id": "c1", "by": "student"}],
    [{"claim_id": "c1", "by": "student", "suggestion_id": "s1"}],
    [{"claim_id": "c1", "by": "coach"}, {"claim_id": "c2", "by": "import"}],
]

BAD_LINKS = [
    {"claim_id": "c1", "by": "student"},                       # not an array
    "c1",
    None,
    ["c1"],                                                    # item not an object
    [None],
    [{"claim_id": "c1", "by": "model"}],
    [{"claim_id": "c1", "by": "mapper"}],
    [{"by": "student"}],                                       # missing claim_id
    [{"claim_id": "c1"}],                                      # missing by
    [{"claim_id": 7, "by": "student"}],
    [{"claim_id": "c1", "by": "student", "score": 1}],         # unknown key
    [{"claim_id": "c1", "by": "coach", "suggestion_id": "s1"}],
    [{"claim_id": "c1", "by": "import", "suggestion_id": "s1"}],
    [{"claim_id": "c1", "by": "student", "suggestion_id": None}],
    [{"claim_id": "c1", "by": "student", "suggestion_id": 3}],
]


@pytest.mark.parametrize("value", GOOD_LINKS)
def test_links_validator_accepts(value):
    from prosemirror.model import Node
    Node.from_json(load_schema(), _para(value)).check()


@pytest.mark.parametrize("value", BAD_LINKS, ids=[json.dumps(v) for v in BAD_LINKS])
def test_links_validator_refuses(value):
    from prosemirror.model import Node
    with pytest.raises(ValueError):
        Node.from_json(load_schema(), _para(value)).check()


@pytest.mark.parametrize("value", BAD_LINKS, ids=[json.dumps(v) for v in BAD_LINKS])
def test_an_attr_step_with_bad_links_is_refused_in_replay(value):
    with pytest.raises(ReplayError):
        replay_steps(_para([]), [_attr_step(value)])


def test_an_attr_step_replays_and_sets_the_links():
    doc = replay_steps(_para([]), [_attr_step([{"claim_id": "c1", "by": "student"}])])
    assert links(doc.to_json()) == [["c1/student"]]


def test_a_replace_around_step_wraps_a_paragraph_and_keeps_its_links():
    start = _para([{"claim_id": "c1", "by": "student"}])
    wrap = {
        "stepType": "replaceAround", "from": 0, "to": 2, "gapFrom": 0, "gapTo": 2,
        "insert": 1, "structure": True,
        "slice": {"content": [{"type": "blockquote"}], "openStart": 0, "openEnd": 0},
    }
    doc = replay_steps(start, [wrap]).to_json()
    assert doc["content"][0]["type"] == "blockquote"
    assert links(doc) == [["c1/student"]]


def test_heading_level_outside_one_to_three_is_refused():
    from prosemirror.model import Node
    schema = load_schema()
    for level in (1, 2, 3):
        Node.from_json(schema, {"type": "doc", "content": [{"type": "heading", "attrs": {"level": level}}]}).check()
    for level in (4, 0, "1", None, True):
        with pytest.raises(ValueError):
            Node.from_json(schema, {"type": "doc", "content": [{"type": "heading", "attrs": {"level": level}}]}).check()


# ---- the step-type allowlist (D-044) ----

def test_the_allowlist_is_the_d044_list():
    assert ALLOWED_STEP_TYPES == {
        "replace", "replaceAround", "addMark", "removeMark",
        "addNodeMark", "removeNodeMark", "attr", "docAttr",
    }


@pytest.mark.parametrize("step", [
    {"stepType": "markSet", "steps": []},
    {"stepType": "nope"},
    {},
])
def test_a_step_type_outside_the_allowlist_is_refused(step):
    c = case("typed_plain")
    with pytest.raises(ReplayError, match="not allowed"):
        replay_steps(c["start"], c["steps"] + [step])


def test_schema_has_the_same_nodes_and_marks_as_the_json():
    spec = json.loads(SCHEMA_JSON.read_text())
    schema = load_schema()
    assert list(schema.nodes) == NODES == list(spec["nodes"])
    assert list(schema.marks) == ["origin", "em", "strong"] == list(spec["marks"])
    assert "claim" not in schema.marks
    assert schema.marks["origin"].spec.get("inclusive") is False


# Steps recorded in real Chromium (spikes/S1/browser_check.mjs; not regenerated in CI).
BROWSER = json.loads((FIXTURE.parent / "s1_browser_steps.json").read_text(encoding="utf-8"))


def test_browser_fixture_covers_the_real_input_paths():
    names = {c["name"] for c in BROWSER["cases"]}
    assert {"kb_inside_quote", "ime_inside_quote", "extension_dom_edit", "copy_paste_internal",
            "paste_external_html", "drag_move_internal", "drop_external", "undo_redo",
            # T-011 link, structure and formatting cases
            "kb_linked_paragraph", "enter_split_linked", "enter_end_linked", "backspace_join_linked",
            "copy_paste_linked_paragraphs", "undo_redo_link", "bold_typing", "list_enter",
            "shift_enter_hard_break"} <= names
    assert all(c["passed"] for c in BROWSER["cases"])


@pytest.mark.parametrize("c", BROWSER["cases"], ids=[c["name"] for c in BROWSER["cases"]])
def test_every_chromium_step_type_is_allowed(c):
    assert {s["stepType"] for s in c["steps"]} <= ALLOWED_STEP_TYPES


@pytest.mark.parametrize("c", BROWSER["cases"], ids=[c["name"] for c in BROWSER["cases"]])
def test_python_replay_matches_chromium(c):
    doc = replay_steps(c["start"], c["steps"])
    assert doc.to_json() == c["doc"]
    assert doc_hash(doc) == c["doc_hash"]
