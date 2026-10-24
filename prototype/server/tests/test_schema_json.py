"""web/schema.json is the one editor schema the Python replay also loads (D33).

These checks guard the parts of event-log.md §4 and D-044 that the file itself
carries: the closed origin list, the paragraph `links` attr, the node set,
and `inclusive: false` (D21). Loading it into prosemirror-py is spike S1's job
(T-004, T-011).
"""

import json
from pathlib import Path

import pytest

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "web" / "schema.json"

ORIGIN_KINDS = ["typed", "paste_ext", "quote", "helper", "coach", "import"]
REF_BY_KIND = {
    "typed": None,
    "paste_ext": "paste_id",
    "quote": "block_id",
    "helper": "helper_serve_id",
    "coach": "q_id",
    "import": "import_id",
}
LINK_BY = ["student", "coach", "import"]
NODES = ["doc", "paragraph", "heading", "blockquote", "bullet_list", "ordered_list",
         "list_item", "text", "hard_break"]


@pytest.fixture(scope="module")
def schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_schema_version_is_two(schema):
    assert schema["x-writing-room"]["schema_version"] == 2
    assert schema["x-writing-room"]["note"]


def test_marks_are_exactly_origin_em_strong(schema):
    assert list(schema["marks"]) == ["origin", "em", "strong"]
    assert "claim" not in schema["marks"]
    assert schema["marks"]["em"] == {}
    assert schema["marks"]["strong"] == {}


def test_nodes_are_exactly_the_d044_list_in_order(schema):
    assert schema["topNode"] == "doc"
    assert list(schema["nodes"]) == NODES


def test_node_structure(schema):
    nodes = schema["nodes"]
    assert nodes["doc"] == {"content": "block+"}
    assert nodes["paragraph"]["group"] == "block" and nodes["paragraph"]["content"] == "inline*"
    assert nodes["blockquote"] == {"group": "block", "content": "block+", "defining": True}
    assert nodes["bullet_list"] == {"group": "block", "content": "list_item+"}
    assert nodes["ordered_list"] == {"group": "block", "content": "list_item+"}
    assert nodes["list_item"] == {"content": "paragraph block*", "defining": True}
    assert nodes["text"] == {"group": "inline"}
    assert nodes["hard_break"] == {"group": "inline", "inline": True, "selectable": False}


def test_heading_level_is_one_to_three(schema):
    heading = schema["nodes"]["heading"]
    assert heading["group"] == "block" and heading["content"] == "inline*" and heading["defining"] is True
    assert heading["attrs"]["level"] == {"default": 1, "validate": "number", "enum": [1, 2, 3]}


def test_paragraph_links_attr(schema):
    attrs = schema["nodes"]["paragraph"]["attrs"]
    assert list(attrs) == ["links"]
    links = attrs["links"]
    assert links["default"] == []
    assert links["validate"] == "array"
    items = links["items"]
    assert list(items) == ["claim_id", "by", "suggestion_id"]
    assert "optional" not in items["claim_id"] and "optional" not in items["by"]
    assert items["by"]["enum"] == LINK_BY
    assert items["suggestion_id"]["optional"] is True
    assert items["suggestion_id"]["only_when"] == {"by": "student"}


def test_origin_kind_is_the_closed_list(schema):
    kind = schema["marks"]["origin"]["attrs"]["kind"]
    assert kind["enum"] == ORIGIN_KINDS
    assert "default" not in kind, "kind must be required, never defaulted"


def test_origin_ref_per_kind_matches_the_design_table(schema):
    origin = schema["marks"]["origin"]
    assert origin["x-ref-by-kind"] == REF_BY_KIND
    assert list(origin["attrs"]) == ["kind", "ref"]
    assert origin["attrs"]["ref"]["default"] is None


def test_origin_is_not_inclusive_d21(schema):
    # Text typed at the edge of a marked span must not inherit the mark.
    assert schema["marks"]["origin"]["inclusive"] is False


def test_one_origin_per_character(schema):
    assert schema["marks"]["origin"]["excludes"] == "origin"
