"""Golden sessions (T-015): rebuild every scripted session from its YAML and committed recording,
run the real pipeline and compare the projection with the frozen expected_receipt.

No browser is needed here; the recordings are committed (see fixtures/README.md)."""
import functools

import pytest

from engine.events import canonical_json
from engine.replay import EMPTY_DOC, doc_hash, load_schema, replay_steps
from golden.build import (BuildError, StaleRecording, build_session, load_recording)
from golden.project import project
from golden.script import (EDITOR_ACTIONS, RECORDED_DIR, ScriptError, editor_actions, editor_actions_sha256,
                           list_sessions, load_blocks, load_script, validate_script)

SESSIONS = list_sessions()
SCRIPTS = {s: load_script(s) for s in SESSIONS}


def has_recording(sid: str) -> bool:
    return (RECORDED_DIR / f"{sid}.json").is_file()


def need_recording(sid: str) -> None:
    if not has_recording(sid):
        pytest.skip("no recording")


@functools.lru_cache(maxsize=None)
def built(sid: str):
    return build_session(sid)


def compare(want: dict, got: dict) -> None:
    bad = [f"{k}:\n  expected {want.get(k)!r}\n  got      {got.get(k)!r}"
           for k in dict.fromkeys([*want, *got]) if want.get(k) != got.get(k)]
    assert not bad, "projection differs from expected receipt\n" + "\n".join(bad)


def test_every_session_has_a_recording():
    missing = [s for s in SESSIONS if not has_recording(s)]
    assert not missing, (f"golden sessions without a committed recording: {missing}; run "
                         "`node golden/record.mjs` from prototype/web")


def test_sessions_exist():
    assert SESSIONS


@pytest.mark.parametrize("sid", SESSIONS)
def test_golden_receipt(sid):
    need_recording(sid)
    res = built(sid)
    compare(SCRIPTS[sid]["expected_receipt"], project(res.l1, res.compile))


PENDING = [pytest.param(s, id=s, marks=pytest.mark.xfail(strict=True,
                                                         reason=SCRIPTS[s]["pending"]["reason"]))
           for s in SESSIONS if "pending" in SCRIPTS[s]]


@pytest.mark.parametrize("sid", PENDING)
def test_golden_pending(sid):
    need_recording(sid)
    res = built(sid)
    compare(SCRIPTS[sid]["pending"]["expected_receipt"], project(res.l1, res.compile))


@pytest.mark.parametrize("sid", SESSIONS)
def test_recording_replays_in_python(sid):
    need_recording(sid)
    rec = load_recording(sid)
    schema = load_schema()
    steps: list = []
    for entry in rec["actions"]:
        steps = steps + entry["steps"]
        doc = replay_steps(EMPTY_DOC, steps, schema)
        assert doc_hash(doc) == entry["doc_hash"], f"action {entry['index']} {entry['action']}"
        assert entry["doc_rev"] == len(steps)
        if entry.get("doc") is not None:
            assert doc_hash(entry["doc"]) == entry["doc_hash"]


@pytest.mark.parametrize("sid", SESSIONS)
def test_recording_is_current(sid):
    need_recording(sid)
    assert load_recording(sid)["editor_actions_sha256"] == editor_actions_sha256(SCRIPTS[sid])


@pytest.mark.parametrize("sid", SESSIONS)
def test_build_is_deterministic(sid):
    need_recording(sid)
    a, b = build_session(sid), build_session(sid)
    assert [e["hash"] for e in a.events] == [e["hash"] for e in b.events]
    assert canonical_json(a.l1) == canonical_json(b.l1)


@pytest.mark.parametrize("sid", SESSIONS)
def test_seal_verifies(sid):
    need_recording(sid)
    res = built(sid)
    assert res.verify["ok"], res.verify
    assert res.events[-1]["type"] == "submit"
    assert res.events[-1]["hash"] == res.seal
    for e in res.events:
        if e["type"] == "editor.batch":
            assert e["ts"].endswith(":00Z"), e["ts"]


@pytest.mark.parametrize("sid", SESSIONS)
def test_mapper_labels_are_well_formed(sid):
    script = SCRIPTS[sid]
    assert script.get("label_status") == "draft_needs_second_person_review"
    created = {a["paragraph_id"] for a in script["actions"]
               if a["action"] in EDITOR_ACTIONS and "paragraph_id" in a}
    claims = {c["claim_id"] for c in script.get("claims") or []}
    for b in script.get("batches") or []:
        for link in b.get("expected_links") or []:
            assert link["paragraph_id"] in b["changed_paragraph_ids"], (b["batch_id"], link)
            assert link["paragraph_id"] in created, (b["batch_id"], link)
            assert link["claim_id"] in claims, (b["batch_id"], link)


# ---- unit tests for the builder, independent of the YAML sessions ---------------------------
from prosemirror.model import Node  # noqa: E402
from prosemirror.transform import Transform  # noqa: E402


def make_recording(script: dict, *, doc_everywhere=True) -> dict:
    """A hand-made recording (typed paragraphs and links only) built with prosemirror-py."""
    schema = load_schema()
    doc = Node.from_json(schema, EMPTY_DOC)
    steps_total = 0
    entries = []
    for e in editor_actions(script):
        tr = Transform(doc)
        n = doc.child_count
        if e["action"] == "type_paragraph":
            node = schema.text(e["text"], [schema.marks["origin"].create({"kind": "typed"})])
            first_empty = n == 1 and doc.child(0).content.size == 0 and e["paragraph_id"] == "p1"
            if first_empty:
                tr.insert(1, node)
            else:
                tr.insert(doc.content.size, schema.nodes["paragraph"].create(None, node))
        elif e["action"] == "link":
            idx = int(e["paragraph_id"][1:]) - 1
            pos = sum(doc.child(i).node_size for i in range(idx))
            tr.set_node_attribute(pos, "links", [{"claim_id": e["claim_id"], "by": e["by"]}])
        else:  # pragma: no cover
            raise AssertionError(e["action"])
        doc = tr.doc
        steps = [s.to_json() for s in tr.steps]
        steps_total += len(steps)
        entry = {"index": e["index"], "action": e["action"], "steps": steps,
                 "input_kind": {"keyboard": len(steps)}, "doc_rev": steps_total,
                 "doc_hash": doc_hash(doc), "paste_id": None, "at": None}
        if doc_everywhere:
            entry["doc"] = doc.to_json()
        entries.append(entry)
    return {"session_id": script["session_id"],
            "editor_actions_sha256": editor_actions_sha256(script), "browser": "hand-made",
            "actions": entries}


def unit_script(*actions, **extra) -> dict:
    return {"schema_version": 1, "session_id": "unit", "claims": [{"claim_id": "c1", "text": "T"}],
            "actions": [dict(a) for a in actions], **extra}


def tp(minute, pid, text):
    return {"minute": minute, "action": "type_paragraph", "paragraph_id": pid, "text": text}


SUBMIT = {"minute": 9, "action": "submit"}


def test_unit_thin_honest_matches_without_a_browser():
    script = load_script("thin-honest")
    res = build_session("thin-honest", recording=make_recording(script))
    compare(script["expected_receipt"], project(res.l1, res.compile))


def test_unit_stale_recording_when_editor_action_changes():
    script = unit_script(tp(0, "p1", "Hello there friend."), SUBMIT)
    rec = make_recording(script)
    changed = unit_script(tp(0, "p1", "Hello there enemy."), SUBMIT)
    with pytest.raises(StaleRecording, match="recording is stale for unit"):
        build_session("unit", recording=rec, script=changed)


def test_unit_script_error_on_quote_not_in_block():
    block_id = next(iter(load_blocks()))
    bad = unit_script({"minute": 0, "action": "insert", "paragraph_id": "p1",
                       "runs": [{"text": "this text is not in the block", "kind": "quote",
                                 "ref": block_id}]}, SUBMIT)
    with pytest.raises(ScriptError, match="exact substring"):
        validate_script(bad, "unit")
    unknown = unit_script({"minute": 0, "action": "insert", "paragraph_id": "p1",
                           "runs": [{"text": "x", "kind": "quote", "ref": "nope"}]}, SUBMIT)
    with pytest.raises(ScriptError, match="unknown block"):
        validate_script(unknown, "unit")


def test_unit_script_error_cases():
    with pytest.raises(ScriptError, match="submit must appear"):
        validate_script(unit_script(tp(0, "p1", "x")), "unit")
    with pytest.raises(ScriptError, match="goes back"):
        validate_script(unit_script(tp(2, "p1", "x"), tp(1, "p2", "y"), SUBMIT), "unit")
    with pytest.raises(ScriptError, match="unknown action"):
        validate_script(unit_script({"minute": 0, "action": "dance"}, SUBMIT), "unit")


def test_unit_clock_seconds_count_earlier_actions_in_the_same_minute():
    script = unit_script(
        tp(0, "p1", "Some words here."),
        {"minute": 1, "action": "open_source", "source_id": "nursing"},
        {"minute": 1, "action": "open_source", "source_id": "cs"}, SUBMIT)
    res = build_session("unit", recording=make_recording(script), script=script)
    stamps = [e["ts"] for e in res.events if e["type"] == "source.open"]
    assert stamps == ["2026-11-02T14:01:00Z", "2026-11-02T14:01:01Z"]
    assert res.events[-1]["ts"] == "2026-11-02T14:09:00Z"


def test_unit_coach_outcome_offsets_are_code_points():
    script = unit_script(
        tp(0, "p1", "Some words here."),
        {"minute": 1, "action": "coach_outcome", "q_id": "q1", "outcome": "answered",
         "parts": [{"text": "a\U0001F600", "kind": "typed"}, {"text": "bc", "kind": "paste_ext"}]},
        SUBMIT)
    res = build_session("unit", recording=make_recording(script), script=script)
    ev = next(e for e in res.events if e["type"] == "coach.outcome")
    assert ev["payload"]["answer_text"] == "a\U0001F600bc"
    assert ev["payload"]["origin_runs"] == [{"from": 0, "to": 2, "kind": "typed"},
                                            {"from": 2, "to": 4, "kind": "paste_ext"}]


def test_unit_checkpoint_without_doc_is_a_build_error():
    script = unit_script(tp(0, "p1", "Some words here."),
                         {"minute": 1, "action": "checkpoint"}, SUBMIT)
    with pytest.raises(BuildError, match="recording has no doc for checkpoint"):
        build_session("unit", recording=make_recording(script, doc_everywhere=False),
                      script=script)


def test_unit_mapper_enabled_is_passed_and_validated():
    script = unit_script(tp(0, "p1", "Some words here."), SUBMIT, mapper_enabled=True)
    res = build_session("unit", recording=make_recording(script), script=script)
    assert res.events[0]["payload"]["mapper_enabled"] is True
    with pytest.raises(ScriptError, match="mapper_enabled must be a bool"):
        validate_script(unit_script(tp(0, "p1", "x"), SUBMIT, mapper_enabled="yes"), "unit")


def test_unit_forged_quote_skips_substring_check_but_not_block_ref():
    block_id = next(iter(load_blocks()))
    run = {"text": "words that are not in the block", "kind": "quote", "ref": block_id,
           "forged": True}
    validate_script(unit_script({"minute": 0, "action": "insert", "paragraph_id": "p1",
                                 "runs": [run]}, SUBMIT), "unit")
    run = dict(run, ref="nope")
    with pytest.raises(ScriptError, match="unknown block"):
        validate_script(unit_script({"minute": 0, "action": "insert", "paragraph_id": "p1",
                                     "runs": [run]}, SUBMIT), "unit")
