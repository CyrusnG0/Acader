"""The receipt compiler end to end (receipt.md sections 2-6), with the LLM stubbed."""
import copy as pycopy
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from prosemirror.model import Fragment, Slice

from app.compile_service import load_snapshot_fn
from app.events_service import EventService
from app.receipt_service import build_stamp, issue_receipt, llm_ask
from engine.events import canonical_json, sha256_hex, verify
from engine.provenance import InMemorySources, L1Config, compile_marks, l1_from_compile
from engine.receipt import (ENGINE_VERSION, LLMUnavailable, OutputRejected, compile_receipt,
                            copy as receipt_copy, prompt_file_hash)
from engine.receipt.wording import banned_hits
from tests.test_replay_compile import Clock, Writer

SERVER = Path(__file__).resolve().parents[1]
ROOT = SERVER.parents[1]
PROTOTYPE = SERVER.parent
LOG = "L1"
BLOCK_TEXT = "Patients need their fluid balance checked at every shift."
REF = "Smith, J. (2020). Fluid balance in adults. Journal of Care, 12, 1-9."
SECRET = "SECRET-ANSWER-TEXT-9183"
FIXED_STAMP = {"version": ENGINE_VERSION, "git_sha": "abc123", "lock_hash": "l" * 64,
               "editor_pair": "tiptap-pm 3.32.0 / prosemirror-py 0.6.1",
               "models": {"receipt_question": "stub"},
               "prompt_hashes": {"receipt_question": "p" * 64}}


@pytest.fixture(autouse=True)
def _stub(monkeypatch):
    monkeypatch.setenv("ROOM_LLM", "stub")


def set_doc(w, paras):
    """Replace the whole document: paras = [(text, [claim ids], origin kind, origin ref)]."""
    def fn(tr, s):
        nodes = []
        for (text, ids, kind, ref) in paras:
            mark = s.marks["origin"].create({"kind": kind, "ref": ref})
            nodes.append(s.nodes["paragraph"].create(
                {"links": [{"claim_id": c, "by": "student"} for c in ids]}, s.text(text, [mark])))
        tr.replace(0, tr.doc.content.size, Slice(Fragment.from_array(nodes), 0, 0))
    w.edit(fn)


def rich_log(*, tool="ChatGPT", title="Fluid balance study", paras=None, mismatch=False,
             helper=None, reason_tag="too_narrow", extra=()):
    clock = Clock()
    svc = EventService(":memory:", clock)
    w = Writer(svc, clock, LOG)

    def add(type_, actor, **payload):
        return svc.append_event(LOG, type=type_, actor=actor, payload=payload)
    add("source.add", "teacher", source_id="s1", origin="teacher", title=title, url=None)
    add("card.create", "student", card_id="c1", text="Fluids matter",
        origin_runs=[{"from": 0, "to": 13, "kind": "typed"}], via="typed", via_ref=None)
    add("card.anchor", "student", card_id="c1", source_id="s1", block_id="b1")
    add("claim.create", "student", claim_id="k1", text="Fluid balance needs checking",
        card_ids=["c1"], parent_claim_id=None)
    add("import.declared", "student", import_id="i1", tool_name=tool, raw_text_ref="r1",
        size_chars=120)
    add("claim.extracted", "system", claim_id="kd", text="Intake should be capped", import_id="i1")
    add("source.view_span", "student", source_id="s1", block_ids=["b1"])
    add("coach.ask", "coach", q_id="q1", case="B", trigger_ref="i1", pillar="logic",
        grounding_ids=["kd"], question="Which source supports this?")
    add("coach.outcome", "student", q_id="q1", outcome="answered", answer_text=SECRET,
        origin_runs=[{"from": 0, "to": len(SECRET), "kind": "typed"}])
    add("coach.ask", "coach", q_id="q2", case="C", trigger_ref="p1", pillar="reading",
        grounding_ids=["b1"], question="What does it show?")
    add("coach.outcome", "student", q_id="q2", outcome="disagreed", answer_text=SECRET + " two",
        origin_runs=[{"from": 0, "to": 5, "kind": "typed"}])
    add("editor.paste", "student", paste_id="pp1", kind="external", size_chars=40)
    add("card.set_aside", "student", card_id="c1", source_id="s1", reason_tag=reason_tag)
    for (t_, a_, p_) in extra:
        add(t_, a_, **p_)
    set_doc(w, paras or [
        ("Fluid balance needs checking every shift.", ["k1"], "typed", None),
        ("Intake should be capped for frail patients.", ["kd"], "typed", None),
        ("So the closing claim rests on my own reading.", [], "typed", None)])
    w.checkpoint()
    if mismatch:
        w.submit(hash=sha256_hex(b"not the document"))
    else:
        w.submit()
    sources = InMemorySources(blocks={"b1": BLOCK_TEXT}, helper=helper or {})
    return svc, sources


def parts(svc, sources, *, reverse=False):
    events = svc.events(LOG)
    result = compile_marks(events, load_snapshot_fn(svc, LOG), sources)
    l1 = l1_from_compile(result, list(reversed(events)) if reverse else events)
    seal = events[result.replay.seal_seq]["hash"]
    return dict(events=list(reversed(events)) if reverse else events, l1=l1,
                doc=result.replay.doc, log_id=LOG, seal_hash=seal, sources=sources,
                stamp=FIXED_STAMP)


def compile_bytes() -> bytes:
    svc, sources = rich_log()
    res, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP)
    return canonical_json(res.receipt)


class Counting:
    def __init__(self, *, down_at=None, reply=None):
        self.calls, self.down_at, self.reply = 0, down_at, reply

    def __call__(self, messages):
        self.calls += 1
        if self.down_at == self.calls:
            raise LLMUnavailable("down")
        return self.reply if self.reply is not None else llm_ask(messages)


# ---------------------------------------------------------------- end to end
def test_issue_receipt_end_to_end_and_verify():
    svc, sources = rich_log()
    res, ev = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP)
    r = res.receipt
    assert ev["type"] == "receipt.issued" and ev["payload"] == res.issued_payload()
    assert r["status"] == "complete" and r["questions_pending"] is False
    assert r["built_from"] == "replay" and r["replay_note"] is None
    assert r["schema"] == 1 and r["version"] == 1
    assert res.receipt_hash == sha256_hex(canonical_json(r))
    assert r["receipt_id"].startswith("r_") and len(r["receipt_id"]) == 18
    assert [q["why"] for q in r["questions"]] == ["untraced_claim", "declared_not_anchored",
                                                  "student_linked_claim"]
    allowed = {"k1", "kd", "b1"}
    for q in r["questions"]:
        assert q["q"] and q["pillar"] == "communication"
        assert q["grounding"] and set(q["grounding"]) <= allowed
        assert q["event_ids"] and q["artifact_ids"]
        assert q["why_text"] == receipt_copy.WHY_TEXT[q["why"]]
        assert q["span"]["from"] < q["span"]["to"]
    assert set(res.artifacts) == {a for q in r["questions"] for a in q["artifact_ids"]}
    events = svc.events(LOG)
    seal = r["seal_hash"]
    v = verify(events, seal, receipt=r, artifacts=res.artifacts)
    assert v.ok, v.problems
    # tampering fails
    bad = pycopy.deepcopy(r)
    bad["summary"]["text"] += " Edited."
    assert not verify(events, seal, receipt=bad, artifacts=res.artifacts).ok
    # an artifact that is cited but not given fails
    assert not verify(events, seal, receipt=r, artifacts={}).ok
    # the sections
    assert r["bands"]["event_ids"] == [r["seal_seq"]]
    assert r["declared"]["by_tool"] == [{"tool_name": "ChatGPT", "count": 1, "size_chars": 120}]
    assert r["declared"]["imports"][0]["event_ids"] == [r["declared"]["event_ids"][0]]
    assert r["facts"]["replacement_edits"]["reported_by"] == "browser"
    assert r["facts"]["replacement_edits"]["lower_bound"] is True
    assert r["blind_spots"] == ["retyped", "offline", "undeclared_outside", "understanding"]
    assert r["reading"]["sources"][0]["title"] == "Fluid balance study"
    assert {m["kind"] for m in r["moments"]} >= {"set_aside", "coach_disagreed"}
    assert all(m["event_ids"] for m in r["moments"])
    assert r["engine"]["flags"] == L1Config().to_json()["flags"]
    assert r["engine"]["thresholds"] == L1Config().to_json()["thresholds"]
    assert r["engine"]["wording_filter"] == {"version": 1, "replaced": 0, "skipped_no_grounding": 0}
    assert "ChatGPT" in r["summary"]["text"] and r["summary"]["text"].endswith(".")


def test_seal_hash_must_name_a_submit():
    svc, sources = rich_log()
    p = parts(svc, sources)
    p["seal_hash"] = p["events"][0]["hash"]
    with pytest.raises(ValueError):
        compile_receipt(ask=None, **p)
    p["seal_hash"] = "nope"
    with pytest.raises(ValueError):
        compile_receipt(ask=None, **p)


def test_post_seal_events_do_not_change_the_receipt():
    svc, sources = rich_log()
    a, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP)
    svc.append_event(LOG, type="note.add", actor="teacher", payload={"text": "later"})
    b, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP)
    assert canonical_json(a.receipt) == canonical_json(b.receipt)


# ---------------------------------------------------------------- determinism
def test_compile_twice_and_from_stored_and_reversed():
    svc, sources = rich_log()
    a, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP)
    b, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP)
    assert canonical_json(a.receipt) == canonical_json(b.receipt)
    c, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP, stored=a.artifacts, ask=None)
    assert canonical_json(c.receipt) == canonical_json(a.receipt)
    assert c.receipt_hash == a.receipt_hash and c.artifacts == a.artifacts
    d = compile_receipt(ask=None, stored=a.artifacts, **parts(svc, sources, reverse=True))
    assert canonical_json(d.receipt) == canonical_json(a.receipt)


def test_corrupted_stored_artifact_is_ignored():
    svc, sources = rich_log()
    a, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP)
    broken = {k: {**v, "body": v["body"] + " "} for k, v in a.artifacts.items()}
    c = compile_receipt(ask=None, stored=broken, **parts(svc, sources))
    assert c.receipt["status"] == "questions_pending"


def test_two_fresh_processes_give_the_same_bytes(tmp_path):
    script = tmp_path / "run.py"
    script.write_text("import sys\nfrom tests.test_receipt_compile import compile_bytes\n"
                      "sys.stdout.write(compile_bytes().hex())\n")
    outs = []
    for seed in ("1", "2"):
        env = {**os.environ, "PYTHONPATH": os.pathsep.join([str(SERVER), str(ROOT)]),
               "PYTHONHASHSEED": seed, "ROOM_LLM": "stub"}
        p = subprocess.run([sys.executable, str(script)], cwd=SERVER, env=env,
                           capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
        outs.append(p.stdout)
    assert outs[0] == outs[1]
    assert bytes.fromhex(outs[0]) == compile_bytes()


# ---------------------------------------------------------------- pending
def test_llm_unavailable_makes_questions_pending_and_stops_asking():
    svc, sources = rich_log()
    ask = Counting(down_at=1)
    res, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP, ask=ask)
    r = res.receipt
    assert ask.calls == 1  # once down, later questions are not asked
    assert r["status"] == "questions_pending" and r["questions_pending"] is True
    assert len(r["questions"]) == 3
    assert all(q["q"] is None and q["pillar"] is None and q["grounding"] == []
               for q in r["questions"])
    assert all(q["why"] and q["why_text"] and q["event_ids"] for q in r["questions"])
    assert res.receipt_hash == sha256_hex(canonical_json(r))
    v = verify(svc.events(LOG), r["seal_hash"], receipt=r, artifacts=res.artifacts)
    assert v.ok, v.problems


def test_ask_none_is_pending():
    svc, sources = rich_log()
    res, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP, ask=None)
    assert res.receipt["status"] == "questions_pending" and res.artifacts == {}


def test_down_midway_keeps_earlier_questions():
    svc, sources = rich_log()
    ask = Counting(down_at=2)
    res, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP, ask=ask)
    qs = res.receipt["questions"]
    assert [q["q"] is None for q in qs] == [False, True, True] and ask.calls == 2


def test_invalid_output_twice_cites_two_artifacts():
    svc, sources = rich_log()
    ask = Counting(reply={"question": "Tell me more.", "pillar": "logic", "cites": ["g1"]})
    res, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP, ask=ask)
    q = res.receipt["questions"][0]
    assert q["q"] is None and len(q["artifact_ids"]) == 2  # the retry prompt differs, so both are kept
    assert res.receipt["status"] == "questions_pending"


def test_invalid_then_valid_cites_two_artifacts():
    svc, sources = rich_log()
    replies = [{"question": "Tell me more.", "pillar": "logic", "cites": ["g1"]}]

    def ask(messages):
        return replies.pop(0) if replies else llm_ask(messages)
    res, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP, ask=ask)
    q = res.receipt["questions"][0]
    assert q["q"] is not None and len(q["artifact_ids"]) == 2
    assert res.receipt["status"] == "complete"
    assert verify(svc.events(LOG), res.receipt["seal_hash"], receipt=res.receipt,
                  artifacts=res.artifacts).ok


def test_output_rejected_then_valid():
    svc, sources = rich_log()
    first = [OutputRejected("not json")]

    def ask(messages):
        if first:
            raise first.pop()
        return llm_ask(messages)
    res, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP, ask=ask)
    assert res.receipt["status"] == "complete"
    assert len(res.receipt["questions"][0]["artifact_ids"]) == 1


def test_llm_ask_maps_boundary_errors(monkeypatch):
    from app import llm
    import app.receipt_service as rs

    def boom(exc):
        def f(*a, **k):
            raise exc
        return f
    monkeypatch.setattr(rs, "complete", boom(llm.LLMSchema("bad")))
    with pytest.raises(OutputRejected):
        llm_ask([])
    monkeypatch.setattr(rs, "complete", boom(llm.LLMTimeout("slow")))
    with pytest.raises(LLMUnavailable):
        llm_ask([])
    monkeypatch.setattr(rs, "complete", boom(llm.LLMAuth("key")))
    with pytest.raises(LLMUnavailable):
        llm_ask([])


# ---------------------------------------------------------------- replay mismatch
def test_replay_mismatch_status():
    svc, sources = rich_log(mismatch=True)
    res, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP)
    r = res.receipt
    assert r["status"] == "replay_mismatch" and r["built_from"] == "browser_copy"
    assert r["replay_note"] == receipt_copy.REPLAY_NOTE
    assert r["questions"] and res.receipt_hash == sha256_hex(canonical_json(r))
    assert verify(svc.events(LOG), r["seal_hash"], receipt=r, artifacts=res.artifacts).ok


# ---------------------------------------------------------------- floats and wording
def walk(node, path=()):
    yield path, node
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, path + (k,))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, path + (i,))


def test_no_floats_anywhere():
    svc, sources = rich_log()
    r = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP)[0].receipt
    assert not [p for p, v in walk(r) if isinstance(v, float)]
    canonical_json(r)


def banned_in(receipt):
    hits = []
    for path, v in walk(receipt):
        if path[:2] == ("engine", "flags"):
            continue
        if isinstance(v, str) and banned_hits(v):
            hits.append((path, v))
        if isinstance(v, dict):
            hits += [(path + (k,), k) for k in v
                     if not (path == ("engine",) and k == "flags") and banned_hits(k)]
    return hits


def test_no_banned_words_in_a_rich_receipt():
    svc, sources = rich_log()
    r = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP)[0].receipt
    assert banned_in(r) == []
    assert r["engine"]["wording_filter"]["replaced"] == 0


def test_banned_tool_and_title_are_replaced():
    svc, sources = rich_log(tool="GhostWriter Pro", title="Detecting sepsis")
    res, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP)
    r = res.receipt
    assert banned_in(r) == []
    assert r["declared"]["imports"][0]["tool_name"] == receipt_copy.FALLBACK_TOOL
    assert r["declared"]["by_tool"][0]["tool_name"] == receipt_copy.FALLBACK_TOOL
    assert r["reading"]["sources"][0]["title"] == receipt_copy.FALLBACK_TITLE
    assert receipt_copy.FALLBACK_TOOL in r["summary"]["text"]
    assert r["engine"]["wording_filter"]["replaced"] >= 2


def test_final_sweep_covers_the_summary(monkeypatch):
    import engine.receipt.compile as rc
    monkeypatch.setattr(rc, "build_summary",
                        lambda *a, **k: {"text": "This was flagged.", "event_ids": [0]})
    svc, sources = rich_log()
    res, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP)
    assert res.receipt["summary"]["text"] == receipt_copy.FALLBACK_TEXT
    assert res.receipt["engine"]["wording_filter"]["replaced"] == 1


def test_sweep_leaves_identifiers_alone():
    svc, sources = rich_log(tool="x")
    res, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP)
    r = res.receipt
    assert r["log_id"] == LOG and r["questions"][0]["paragraph_id"] == "p3"
    assert r["questions"][0]["grounding"][0] in ("k1", "kd", "b1")


# ---------------------------------------------------------------- D-046
def test_coach_section_is_counts_and_outcomes_only():
    svc, sources = rich_log()
    r = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP)[0].receipt
    keys = {str(p[-1]) for p, _ in walk(r["coach"]) if p and isinstance(p[-1], str)}
    assert not [k for k in keys if re.search(r"grade|score|resolved|ratio|first|order", k)]
    assert r["coach"]["asked"] == 2
    assert r["coach"]["by_outcome"]["answered"] == 1 and r["coach"]["by_outcome"]["disagreed"] == 1
    assert SECRET not in json.dumps(r, ensure_ascii=False)
    for q in r["coach"]["questions"]:
        assert set(q) == {"q_id", "case", "pillar", "outcome", "event_ids"}


# ---------------------------------------------------------------- mechanics
def test_mechanics_words_are_counted_apart():
    paras = [("Fluid balance needs checking every shift.", ["k1"], "typed", None),
             (REF, [], "helper", "h1")]
    svc, sources = rich_log(paras=paras, helper={"h1": REF})
    r = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP)[0].receipt
    assert r["bands"]["mechanics"] == len(REF.split()) > 0
    assert r["bands"]["total_words"] == len("Fluid balance needs checking every shift.".split())
    assert "words of references and formatting are counted apart" in r["summary"]["text"]


# ---------------------------------------------------------------- stamp
def test_build_stamp():
    s = build_stamp(git_sha="abc")
    lock = (PROTOTYPE / "requirements.lock").read_bytes()
    assert s["git_sha"] == "abc" and s["version"] == ENGINE_VERSION
    assert s["lock_hash"] == hashlib.sha256(lock).hexdigest()
    assert s["editor_pair"] == "tiptap-pm 3.32.0 / prosemirror-py 0.6.1"
    assert s["prompt_hashes"] == {"receipt_question": prompt_file_hash()}
    assert s["prompt_hashes"]["receipt_question"] == hashlib.sha256(
        (SERVER / "engine/receipt/prompts/receipt_question.v1.txt").read_bytes()).hexdigest()
    assert s["models"] == {"receipt_question": "stub"}
    assert set(s) == {"version", "git_sha", "lock_hash", "editor_pair", "models", "prompt_hashes"}


def test_stamp_git_sha_falls_back(monkeypatch):
    monkeypatch.setenv("ROOM_GIT_SHA", "fromenv")
    assert build_stamp()["git_sha"] == "fromenv"
    monkeypatch.delenv("ROOM_GIT_SHA")
    assert build_stamp()["git_sha"]


def test_engine_section_copies_stamp_and_config():
    svc, sources = rich_log()
    r = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP)[0].receipt
    e = r["engine"]
    assert {k: e[k] for k in FIXED_STAMP} == FIXED_STAMP
    assert e["flags"] == L1Config().to_json()["flags"]
    assert e["thresholds"] == L1Config().to_json()["thresholds"]


# ---------------------------------------------------------------- review fixes
def test_reason_tag_is_swept():
    svc, sources = rich_log(reason_tag="suspect data")
    res, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP)
    tags = [m["reason_tag"] for m in res.receipt["moments"] if m["kind"] == "set_aside"]
    assert tags == [receipt_copy.FALLBACK_TEXT]
    assert res.receipt["engine"]["wording_filter"]["replaced"] == 1
    assert banned_in(res.receipt) == []


def test_summary_does_not_use_edit_batches_or_count_days():
    svc, sources = rich_log()
    r = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP)[0].receipt
    batches = {e["seq"] for e in svc.events(LOG) if e["type"] == "editor.batch"
               and e["seq"] <= r["seal_seq"]}
    assert batches
    assert not (batches & set(r["summary"]["event_ids"]))
    assert "Written on" not in r["summary"]["text"]
    assert not re.search(r"\b(?:days?|sessions?|durations?|hours?|minutes?|weeks?)\b",
                         r["summary"]["text"], re.I)


def test_map_finding_question_with_mapper_artifact_verifies():
    body = json.dumps({"finding": "unconnected"})
    art = {"body": body, "hash": sha256_hex(body.encode())}
    first = "Fluid balance needs checking every shift."
    mid = "A middle paragraph that stands alone."
    p2_from = 1 + len(first) + 2
    extra = [("map.finding", "system", {
        "finding_id": "f1", "kind": "unconnected_paragraph",
        "span": {"from": p2_from, "to": p2_from + len(mid)},
        "artifact_id": "a_map1", "output_hash": art["hash"]})]
    paras = [(first, ["k1"], "typed", None), (mid, [], "typed", None),
             ("Last point stands here.", ["k1"], "typed", None)]
    svc, sources = rich_log(paras=paras, extra=extra)
    res, _ = issue_receipt(svc, LOG, sources, stamp=FIXED_STAMP)
    r = res.receipt
    fq = [q for q in r["questions"] if q["why"] == "map_finding_unconnected_paragraph"]
    assert len(fq) == 1 and "a_map1" in fq[0]["artifact_ids"]
    events = svc.events(LOG)
    assert verify(events, r["seal_hash"], receipt=r,
                  artifacts={**res.artifacts, "a_map1": art}).ok
    assert not verify(events, r["seal_hash"], receipt=r, artifacts=res.artifacts).ok
