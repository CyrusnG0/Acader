"""Golden sessions (T-015): rebuild every scripted session from its YAML and committed recording,
run the real pipeline and compare the projection with the frozen expected_receipt.

No browser is needed here; the recordings are committed (see fixtures/README.md)."""
import functools

import pytest

from engine.events import canonical_json, sha256_hex, verify
from engine.replay import EMPTY_DOC, doc_hash, load_schema, replay_steps
from engine.receipt import compile_receipt
from golden.build import (BuildError, StaleRecording, build_session, load_recording)
from golden.project import project, project_compiled
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


@pytest.mark.parametrize("sid", SESSIONS)
def test_compiled_receipt_targets(sid):
    res = built(sid)
    script = SCRIPTS[sid]
    compare(script["expected_compiled_receipt"], project_compiled(res.receipt))
    compare_compiled_counts(script["expected_receipt"], res.receipt)


def compare_compiled_counts(expected: dict, receipt: dict) -> None:
    """Check actual compiler forwarding against the independently authored L1 gold."""
    compare({
        "total_words": expected["total_words"],
        "by_words": expected["bands_by_words"],
        "by_claims": expected["bands_by_claims"],
        "quoted_words": expected["quoted_words"],
        "mechanics": expected["mechanics_words"],
        "inferred_links": expected["inferred_links"],
        "map_suggestions": expected["map_suggestions"],
    }, {
        **{k: receipt["bands"][k] for k in
           ("total_words", "by_words", "by_claims", "quoted_words", "mechanics")},
        "inferred_links": receipt["inferred_links"],
        "map_suggestions": receipt["map_suggestions"],
    })


@pytest.mark.parametrize("sid", SESSIONS)
def test_compiled_receipt_verifies(sid):
    res = built(sid)
    assert res.receipt_hash == sha256_hex(canonical_json(res.receipt))
    issued = res.receipt_events[-1]
    assert issued["type"] == "receipt.issued"
    assert issued["payload"]["receipt_hash"] == res.receipt_hash
    checked = verify(res.receipt_events, res.seal, receipt=res.receipt, artifacts=res.artifacts)
    assert checked.ok, checked.problems
    assert all(q["q"] is not None and q["grounding"] for q in res.receipt["questions"])


@pytest.mark.parametrize("sid", SESSIONS)
def test_stored_receipt_recompile_makes_no_llm_calls(sid):
    res = built(sid)

    def forbidden(_):
        raise AssertionError("stored receipt replay attempted an LLM call")

    replayed = compile_receipt(
        events=res.receipt_events, l1=res.l1, doc=res.doc, log_id=sid,
        seal_hash=res.seal, sources=res.sources, stamp=res.stamp,
        ask=forbidden, stored=res.artifacts)
    assert canonical_json(replayed.receipt) == canonical_json(res.receipt)
    assert replayed.receipt_hash == res.receipt_hash
    offline = compile_receipt(
        events=res.receipt_events, l1=res.l1, doc=res.doc, log_id=sid,
        seal_hash=res.seal, sources=res.sources, stamp=res.stamp,
        ask=None, stored=res.artifacts)
    assert canonical_json(offline.receipt) == canonical_json(res.receipt)


@pytest.mark.parametrize("sid", SESSIONS)
def test_questions_pending_preserves_selected_targets(sid):
    res = built(sid)
    pending = build_session(sid, ask=None)
    assert [q["paragraph_id"] for q in pending.receipt["questions"]] == [
        q["paragraph_id"] for q in res.receipt["questions"]]
    assert [q["why"] for q in pending.receipt["questions"]] == [
        q["why"] for q in res.receipt["questions"]]
    assert all(q["q"] is None for q in pending.receipt["questions"])
    expected = bool(res.receipt["questions"])
    assert pending.receipt["questions_pending"] is expected
    assert pending.receipt["status"] == ("questions_pending" if expected else "complete")
    assert verify(pending.receipt_events, pending.seal, receipt=pending.receipt,
                  artifacts=pending.artifacts).ok


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
    assert canonical_json(a.receipt) == canonical_json(b.receipt)
    assert a.receipt_hash == b.receipt_hash
    assert a.artifacts == b.artifacts
    assert [e["hash"] for e in a.receipt_events] == [e["hash"] for e in b.receipt_events]


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


def test_builder_refuses_live_llm_mode(monkeypatch):
    monkeypatch.delenv("ROOM_LLM", raising=False)
    with pytest.raises(BuildError, match="require ROOM_LLM=stub"):
        build_session("honest-nursing")


def test_receipt_verification_rejects_missing_mapper_artifact():
    res = built("accepted-suggestion-paste")
    missing = {k: v for k, v in res.artifacts.items() if k != "artifact-sg1"}
    checked = verify(res.receipt_events, res.seal, receipt=res.receipt, artifacts=missing)
    assert not checked.ok
    assert "artifact artifact-sg1 is not stored" in checked.problems


def test_receipt_verification_rejects_changed_receipt():
    res = built("honest-nursing")
    changed = {**res.receipt, "summary": {**res.receipt["summary"], "text": "Changed."}}
    assert not verify(res.receipt_events, res.seal, receipt=changed,
                      artifacts=res.artifacts).ok


@pytest.mark.parametrize("field", ["expected_receipt", "expected_compiled_receipt"])
def test_show_cli_fails_on_either_projection_mismatch(monkeypatch, capsys, field):
    import copy
    from golden import __main__ as cli

    script = copy.deepcopy(SCRIPTS["honest-nursing"])
    script[field]["status"] = "incorrect_expected_status"
    monkeypatch.setattr(cli, "load_script", lambda sid: script)
    assert cli.main(["show", "honest-nursing"]) == 1
    assert f"DIFF {field}.status" in capsys.readouterr().out


def test_actions_cli_does_not_need_stub_mode(monkeypatch, capsys):
    from golden import __main__ as cli

    monkeypatch.delenv("ROOM_LLM", raising=False)
    assert cli.main(["actions", "honest-nursing"]) == 0
    assert "type_paragraph" in capsys.readouterr().out


def test_compiled_count_assertion_rejects_misforwarded_band():
    import copy

    receipt = copy.deepcopy(built("honest-nursing").receipt)
    receipt["bands"]["by_words"]["traced_source"] += 1
    with pytest.raises(AssertionError, match="by_words"):
        compare_compiled_counts(SCRIPTS["honest-nursing"]["expected_receipt"], receipt)


@pytest.mark.parametrize("sid", SESSIONS)
def test_golden_receipt_has_registered_source_metadata(sid):
    from golden.script import load_sources

    res = built(sid)
    ids = SCRIPTS[sid]["source_ids"]
    manifest = load_sources()
    adds = [e for e in res.events if e["type"] == "source.add"]
    assert [e["payload"]["source_id"] for e in adds] == ids
    assert all(e["actor"] == "teacher" for e in adds)
    first_student = next(e["seq"] for e in res.events if e["actor"] == "student")
    assert all(e["seq"] < first_student for e in adds)
    for event in adds:
        source = manifest[event["payload"]["source_id"]]
        assert event["payload"] == {"source_id": source["id"], "origin": "teacher",
                                    "title": source["title"], "url": source["content_url"]}
    reading = {r["source_id"]: r for r in res.receipt["reading"]["sources"]}
    assert set(reading) == set(ids)
    for source_id in ids:
        assert reading[source_id]["title"] == manifest[source_id]["title"]
    count_phrase = "with 1 source" if len(ids) == 1 else f"with {len(ids)} sources"
    assert count_phrase in res.receipt["summary"]["text"]
    assert "with no sources" not in res.receipt["summary"]["text"]
    assert {e["seq"] for e in adds} <= set(res.receipt["summary"]["event_ids"])


@pytest.mark.parametrize("ids, message", [
    (["not-in-manifest"], "unknown source_ids"),
    (["nursing", "nursing"], "duplicate source_ids"),
    ("nursing", "list of strings"),
    ([1], "list of strings"),
    (None, "list of strings"),
])
def test_invalid_source_ids_rejected_before_build(ids, message):
    script = unit_script(tp(0, "p1", "Some words here."), SUBMIT, source_ids=ids)
    with pytest.raises(ScriptError, match=message):
        validate_script(script, "unit")
    with pytest.raises(ScriptError, match=message):
        build_session("unit", recording=make_recording(script), script=script)


def test_unit_script_without_source_ids_still_builds():
    script = unit_script(tp(0, "p1", "Some words here."), SUBMIT)
    validate_script(script, "unit")
    res = build_session("unit", recording=make_recording(script), script=script)
    assert not any(e["type"] == "source.add" for e in res.events)
    assert res.receipt["reading"]["sources"] == []
