"""web/schema.json is the one editor schema the Python replay also loads (D33).

These checks guard the parts of event-log.md §4 that the file itself carries:
the closed origin list, the claim mark attrs, and `inclusive: false` (D21).
Loading it into prosemirror-py is spike S1's job (T-004).
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
CLAIM_BY = ["student", "coach", "import"]


@pytest.fixture(scope="module")
def schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_schema_has_only_origin_and_claim_marks(schema):
    assert list(schema["marks"]) == ["origin", "claim"]
    assert schema["topNode"] == "doc"
    assert "text" in schema["nodes"]


def test_origin_kind_is_the_closed_list(schema):
    kind = schema["marks"]["origin"]["attrs"]["kind"]
    assert kind["enum"] == ORIGIN_KINDS
    assert "default" not in kind, "kind must be required, never defaulted"


def test_origin_ref_per_kind_matches_the_design_table(schema):
    origin = schema["marks"]["origin"]
    assert origin["x-ref-by-kind"] == REF_BY_KIND
    assert list(origin["attrs"]) == ["kind", "ref"]
    assert origin["attrs"]["ref"]["default"] is None


def test_claim_mark_attrs(schema):
    attrs = schema["marks"]["claim"]["attrs"]
    assert list(attrs) == ["claim_id", "by", "suggestion_id"]
    assert "default" not in attrs["claim_id"]
    assert "default" not in attrs["by"]
    assert attrs["by"]["enum"] == CLAIM_BY
    assert attrs["suggestion_id"]["default"] is None


@pytest.mark.parametrize("mark", ["origin", "claim"])
def test_marks_are_not_inclusive_d21(schema, mark):
    # Text typed at the edge of a marked span must not inherit the mark.
    assert schema["marks"][mark]["inclusive"] is False


@pytest.mark.parametrize("mark", ["origin", "claim"])
def test_one_mark_of_each_type_per_character(schema, mark):
    assert schema["marks"][mark]["excludes"] == mark

