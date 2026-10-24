"""Spike S1: Python replay parity (evaluation.md §1, event-log.md §5, D6, D33).

The fixture is written by the browser editor test (web/src/editor/s1.test.ts):
each case holds the start doc, the steps TipTap recorded, the browser's final
doc and its doc_hash. prosemirror-py, loading the same web/schema.json, must
replay the steps to the same doc, the same marks and the same hash.
"""
import copy
import json
from pathlib import Path

import pytest

from engine.replay import ReplayError, doc_hash, load_schema, replay_steps

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "replay" / "s1_steps.json"
DATA = json.loads(FIXTURE.read_text(encoding="utf-8"))
CASES = DATA["cases"]
IDS = [c["name"] for c in CASES]

# The cases the spike must cover (evaluation.md §1). Dropping one from the
# editor test makes this list fail.
REQUIRED = {
    "typed_plain", "typed_inside_quote", "typed_inside_paste_ext", "typed_inside_helper",
    "typed_inside_coach", "typed_inside_import", "typed_edges_quote", "typed_between_spans",
    "typed_claim_student", "typed_claim_coach", "typed_claim_import", "select_all_type",
    "typed_astral", "split_paragraph", "delete_across_edge", "replacement_in_quote",
    "ime_in_quote", "dom_edit_in_quote", "paste_external_html", "paste_external_in_quote",
    "copy_paste_internal", "cut_paste_move", "paste_other_log", "paste_malformed_slice",
    "drag_move_internal", "drop_external", "undo_redo", "keystroke_handle_text_input",
}


def runs(doc_json):
    """[(text, origin kind, ref, claim)] per paragraph."""
    out = []
    for para in doc_json.get("content", []):
        row = []
        for t in para.get("content", []):
            marks = {m["type"]: m.get("attrs", {}) for m in t.get("marks", [])}
            o, c = marks.get("origin"), marks.get("claim")
            row.append((t["text"], o and o["kind"], o and o.get("ref"),
                        c and f'{c["claim_id"]}/{c["by"]}'))
        out.append(row)
    return out


def test_fixture_covers_every_s1_case():
    assert REQUIRED <= set(IDS)
    assert DATA["schema_version"] == json.loads(
        (Path(__file__).resolve().parents[2] / "web" / "schema.json").read_text())["x-writing-room"]["schema_version"]


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_python_replay_matches_browser(case):
    doc = replay_steps(case["start"], case["steps"])
    assert doc.to_json() == case["doc"]
    assert doc_hash(doc) == case["doc_hash"]


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_every_character_has_exactly_one_origin(case):
    for para in case["doc"].get("content", []):
        for t in para.get("content", []):
            assert [m["type"] for m in t.get("marks", [])].count("origin") == 1, t


def test_typed_inside_a_span_is_typed_in_the_replayed_doc():
    case = next(c for c in CASES if c["name"] == "typed_claim_coach")
    doc = replay_steps(case["start"], case["steps"]).to_json()
    assert runs(doc) == [[
        ("[", "typed", None, None),
        ("cla", "quote", "b81", "c3/coach"),
        ("_", "typed", None, None),
        ("imed", "quote", "b81", "c3/coach"),
        ("]", "typed", None, None),
    ]]


def test_external_paste_is_paste_ext_in_the_replayed_doc():
    case = next(c for c in CASES if c["name"] == "paste_external_html")
    doc = replay_steps(case["start"], case["steps"]).to_json()
    assert runs(doc) == [[("x", "typed", None, None),
                          ("outside forged bold", "paste_ext", "log_A_paste_1", None)]]


def test_astral_positions_match():
    case = next(c for c in CASES if c["name"] == "typed_astral")
    doc = replay_steps(case["start"], case["steps"]).to_json()
    assert [r[0] for r in runs(doc)[0]] == ["café 😀", "🎓!", " naïve"]


def test_a_changed_step_breaks_parity():
    case = copy.deepcopy(next(c for c in CASES if c["name"] == "typed_inside_quote"))
    add = next(s for s in case["steps"] if s["stepType"] == "addMark")
    add["mark"]["attrs"]["kind"] = "quote"
    add["mark"]["attrs"]["ref"] = "b81"
    doc = replay_steps(case["start"], case["steps"])
    assert doc.to_json() != case["doc"]
    assert doc_hash(doc) != case["doc_hash"]


def test_dropping_a_step_breaks_parity():
    case = copy.deepcopy(next(c for c in CASES if c["name"] == "undo_redo"))
    last_replace = max(i for i, s in enumerate(case["steps"]) if s["stepType"] == "replace")
    del case["steps"][last_replace]
    doc = replay_steps(case["start"], case["steps"])
    assert doc_hash(doc) != case["doc_hash"]


def test_a_kind_outside_the_closed_list_is_refused():
    case = copy.deepcopy(next(c for c in CASES if c["name"] == "typed_plain"))
    add = next(s for s in case["steps"] if s["stepType"] == "addMark")
    add["mark"]["attrs"]["kind"] = "ai"
    with pytest.raises(ReplayError):
        replay_steps(case["start"], case["steps"])


def test_a_claim_by_outside_the_closed_list_is_refused():
    from prosemirror.model import Mark
    schema = load_schema()
    Mark.from_json(schema, {"type": "claim", "attrs": {"claim_id": "c1", "by": "student"}})
    with pytest.raises(ValueError):
        Mark.from_json(schema, {"type": "claim", "attrs": {"claim_id": "c1", "by": "model"}})


def test_an_unknown_step_type_is_refused():
    case = next(c for c in CASES if c["name"] == "typed_plain")
    with pytest.raises(ReplayError):
        replay_steps(case["start"], case["steps"] + [{"stepType": "markSet", "steps": []}])


def test_schema_has_the_same_nodes_and_marks_as_the_json():
    spec = json.loads((Path(__file__).resolve().parents[2] / "web" / "schema.json").read_text())
    schema = load_schema()
    assert set(schema.nodes) == set(spec["nodes"])
    assert set(schema.marks) == set(spec["marks"])
    assert schema.marks["origin"].spec.get("inclusive") is False
    assert schema.marks["claim"].spec.get("inclusive") is False


# Steps recorded in real Chromium (spikes/S1/browser_check.mjs; not regenerated in CI).
BROWSER = json.loads((FIXTURE.parent / "s1_browser_steps.json").read_text(encoding="utf-8"))


def test_browser_fixture_covers_the_real_input_paths():
    names = {c["name"] for c in BROWSER["cases"]}
    assert {"kb_inside_quote", "ime_inside_quote", "extension_dom_edit", "copy_paste_internal",
            "paste_external_html", "drag_move_internal", "drop_external", "undo_redo"} <= names
    assert all(c["passed"] for c in BROWSER["cases"])


@pytest.mark.parametrize("case", BROWSER["cases"], ids=[c["name"] for c in BROWSER["cases"]])
def test_python_replay_matches_chromium(case):
    doc = replay_steps(case["start"], case["steps"])
    assert doc.to_json() == case["doc"]
    assert doc_hash(doc) == case["doc_hash"]
