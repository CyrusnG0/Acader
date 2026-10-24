import json, re
import pytest
import llmx, room, lineage, finalize, score, audit

def src_flow(texts, clear=True, picks=None):
    s = room.new_session("T", "C1")
    llmx.HANDLERS["src_pick"] = lambda sy, u: json.dumps({"need_clear": clear, "pick": picks() if picks else ["D1", "D2", "D3", "D4"]})
    for t in texts: room.cmd_say(s, t)
    return room.load("T")

def test_1_serves_after_stable_pick():
    s = src_flow(["find me a source", "I need rent data for my claim about supply"])
    r = s["src_requests"][0]
    assert r["state"] == "served" and r["served_after_cap"] is False and 3 <= len(r["shortlist"]) <= 5

def test_2_serves_at_cap():
    n = iter(range(100))
    s = src_flow(["find me a source"] + ["not sure yet"] * 4, clear=False, picks=lambda: [f"D{next(n) % 12 + 1}" for _ in range(4)])
    r = s["src_requests"][0]
    assert r["state"] == "served" and r["served_after_cap"] is True and r["clarify_turns"] == 3

def test_3_clarify_prompts_hold_no_corpus():
    src_flow(["find me a source", "still unsure", "hmm"], clear=False, picks=lambda: ["D1", "D2", "D3"])
    clar = [c for c in llmx.CAPTURED if c["tag"] == "src_clarify"]
    assert clar
    titles = [d["title"] for d in room.CORPUS]
    for c in clar:
        blob = c["system"] + c["user"]
        assert not re.search(r"\bD\d{1,2}(p\d+)?\b", blob)
        assert not any(t.lower() in blob.lower() for t in titles)
        assert not any(p[:40] in blob for p in room.PASSAGES.values())

def test_4_pick_refusals():
    s = src_flow(["find me a source", "rent data for my claim"])
    short = s["last_shortlist"]
    assert "why" in room.cmd_pick(s, short[0], "ok").lower()          # 1-word reason
    assert "why" in room.cmd_pick(s, short[0], "seems good").lower()  # 2 words
    outside = [d for d in room.DOCS if d not in short][0]
    assert "not on the list" in room.cmd_pick(s, outside, "because it has data on rents")
    assert s["unlocked_docs"] == []
    assert "Unlocked" in room.cmd_pick(s, short[0], "it has rent data for my claim")
    assert short[0] in s["unlocked_docs"]

def test_5_read_refuses_locked():
    s = room.new_session("T", "C1")
    assert "locked" in room.cmd_read(s, "D3p1")
    s["unlocked_docs"].append("D3")
    assert room.cmd_read(s, "D3p1").startswith("[D3p1]")
    assert "D3p1" in s["read_passages"]

def test_6_write_request_counts_and_never_writes():
    llmx.HANDLERS["route"] = lambda sy, u: json.dumps({"intent": "write_request", "question_kind": "wants_answer"})
    s = room.new_session("T", "C1")
    out = room.cmd_say(s, "write my intro")
    assert s["counters"]["write_requests"] == 1 and "idea" in out.lower()
    assert "essay prose" not in out.lower()
    room.cmd_say(s, "just write it")
    assert s["counters"]["write_requests"] == 2

def test_7_change_lineage_three_drafts():
    d1 = "Para one about rent.\n\nPara two about supply."
    d2 = "Para one about rent.\n\nA wholly different second paragraph on landlords and compensation law."
    final = d2 + "\n\nBrand new closing paragraph concerning rehousing pathways."
    assert [c["para"] for c in lineage.changed_paragraphs("", d1)] == [1, 2]
    assert [c["para"] for c in lineage.changed_paragraphs(d1, d2)] == [2]
    assert [c["para"] for c in lineage.changed_paragraphs(d2, final)] == [3]
    turns = [{"i": i, "who": "student", "kind": "say", "text": f"t{i}", "paste": False} for i in range(9)]
    run = {"essay": final, "drafts": [{"text": d1, "turn": 3}, {"text": d2, "turn": 6}], "turns": turns}
    snaps = lineage.snapshots(run)
    assert [(a, b) for _, _, a, b in snaps] == [(0, 3), (3, 6), (6, 9)]
    llmx.HANDLERS["change"] = lambda sy, u: json.dumps({"results": [{"n": 1, "discussed": True}, {"n": 2, "discussed": True}, {"n": 3, "discussed": False}]})
    sc, det = lineage.change_lineage(run, lineage.student_statements(turns))
    assert len(det) == 4 and sum(d["discussed"] for d in det) == 3   # 2 + 1 + 1 changed paragraphs; 3 discussed
    assert sc == 75.0

def test_8_source_lineage():
    run = {"citations": [{"pid": "D3p1", "pos": 0}, {"pid": "D3p2", "pos": 5}, {"pid": "D5p1", "pos": 9}],
           "picks": [{"docs": ["D3"], "reason": "first-hand account of rent"}, {"docs": ["D5"], "reason": "ok"}]}
    sc, missing = lineage.source_lineage(run)
    assert sc == 50.0 and missing == ["D5"]   # D5 picked with a 1-word reason does not count

def test_9_struct_rule():
    essay = "word " * 600
    t = finalize.struct_record("typed", essay, "x")
    assert t["paste_chars"] == 0 and t["bursts"] == 10
    p = finalize.struct_record("pasted", essay, "x")
    assert p["paste_chars"] == len(essay) + 100 and 1 <= p["bursts"] <= 3
    assert lineage.struct_score({"struct": p, "essay": essay}) == 0.0
    assert lineage.struct_score({"struct": t, "essay": essay}) == 100.0
    s = {"arm": "C3", "id": "C3-1", "question": "q", "drafts": [], "turns": [], "src_requests": [], "picks": [],
         "unlocked_docs": [], "read_passages": [], "counters": {"write_requests": 0, "claim_statements": 0}, "question_kinds": []}
    with pytest.raises(SystemExit): finalize.build(s, "essay [D1p1]", struct="typed")
    assert finalize.build(s, "essay [D1p1]")["struct"]["kind"] == "pasted"
    with pytest.raises(SystemExit): finalize.build(s, "no citations here")

def test_10_lineage_prompts_carry_no_arm_or_id():
    turns = [{"i": 0, "who": "student", "kind": "say", "text": "I think rents rose", "paste": False}]
    run = {"id": "C4-9", "arm": "C4", "question": "q", "essay": "Rents rose [D2p1].", "citations": [{"pid": "D2p1", "pos": 14}],
           "struct": {"kind": "retyped", "paste_chars": 0, "bursts": 6}, "drafts": [], "turns": turns, "src_requests": [],
           "picks": [], "unlocked_docs": [], "read_passages": [], "counters": {"write_requests": 0}, "question_kinds": [], "flags": {"x": 1}}
    llmx.CAPTURED.clear()
    rep = lineage.report(lineage.strip(run))
    assert llmx.CAPTURED
    for c in llmx.CAPTURED:
        assert "C4-9" not in c["system"] + c["user"] and '"arm"' not in c["user"]
    assert "composite_nostruct" in rep
    banned = re.compile(r"detect|cheat|catch|monitor", re.I)
    assert not banned.search(json.dumps(rep["mismatches"]))

def test_11_auc_known_inputs():
    assert score.auc([3, 4], [1, 2]) == 1.0
    assert score.auc([1, 2], [3, 4]) == 0.0
    assert score.auc([1, 2], [1, 2]) == 0.5
    lo, hi = score.boot_ci([3, 4, 5, 6], [1, 2, 3, 0])
    assert 0.5 <= lo <= hi <= 1.0

def test_audit_leak_check():
    turns = [{"i": 1, "who": "assistant", "kind": "reply", "text": "Maybe look at D3 for that.", "state": "clarify"},
             {"i": 3, "who": "assistant", "kind": "reply", "text": "What should it show?", "state": "clarify"}]
    assert [l["turn"] for l in audit.clarify_turn_leaks(turns)] == [1]

def test_12_open_shortlist_gets_a_reminder_then_a_new_request():
    s = src_flow(["find me a source", "rent data for my claim"])
    assert s["src_requests"][0]["state"] == "served"
    out = room.cmd_say(s, "find me a different source")
    assert "still open" in out and len(s["src_requests"]) == 1
    room.cmd_say(s, "find me a different source please")
    assert len(s["src_requests"]) == 2 and s["src_requests"][0]["state"] == "abandoned"


# ---------------- v0.5 tests ----------------
import os
import lineage2, derive, effort, relay, controls

def _run(essay, drafts, turns):
    return {"essay": essay, "drafts": drafts, "turns": turns, "citations": [], "picks": [], "struct": {"kind": "retyped", "paste_chars": 0, "bursts": 6},
            "src_requests": [], "unlocked_docs": [], "read_passages": [], "counters": {"write_requests": 0}, "question_kinds": []}

ESSAY = "Rents in subdivided units rose sharply after the rule changed.\n\nLandlords responded by converting additional flats quickly."
def _turns(n, kinds=None):
    return [{"i": i, "who": "student", "kind": (kinds or {}).get(i, "say"), "text": f"t{i}", "paste": False} for i in range(n)]

def test_13_timing_rule_kinds():
    assert lineage2.kind_of(None, 5) == "none"
    assert lineage2.kind_of(3, 5) == "derived"
    assert lineage2.kind_of(5, 5) == "explained_after"      # at the birth turn is not before it
    assert lineage2.kind_of(9, 5) == "explained_after"

def test_14_birth_turn_is_first_matching_snapshot():
    drafts = [{"turn": 3, "text": "Something unrelated about transport.", "struct": "retyped"},
              {"turn": 6, "text": ESSAY.split("\n\n")[0], "struct": "retyped"},
              {"turn": 8, "text": ESSAY, "struct": "retyped"}]
    run = _run(ESSAY, drafts, _turns(10))
    claim = {"para": 1, "claim": "Rents in subdivided units rose sharply after the rule changed.", "ancestor": 2}
    assert lineage2.birth_turn(claim, run) == 6
    c2 = {"para": 2, "claim": "Landlords converted additional flats quickly.", "ancestor": 1}
    assert lineage2.birth_turn(c2, run) == 8
    c3 = {"para": 2, "claim": "Completely different words entirely absent elsewhere.", "ancestor": None}
    assert lineage2.birth_turn(c3, run) == 10                # no snapshot qualifies: the final turn

def test_15_answer_after_birth_is_explained_after():
    turns = _turns(9, {7: "answer"})
    run = _run(ESSAY, [{"turn": 5, "text": ESSAY, "struct": "retyped", "check": True}], turns)
    llmx.HANDLERS["claims"] = lambda sy, u: json.dumps({"claims": [{"para": 1, "claim": "Rents in subdivided units rose sharply after the rule changed."}]})
    llmx.HANDLERS["ancestor"] = lambda sy, u: json.dumps({"results": [{"n": 1, "turn": 7}]})
    rep = lineage2.report2(run)
    assert rep["claims"][0]["kind"] == "explained_after" and rep["explained_after"] and rep["report_version"] == "v2"
    assert rep["components"]["claim_v2"] == 0.0
    llmx.HANDLERS["ancestor"] = lambda sy, u: json.dumps({"results": [{"n": 1, "turn": 2}]})
    assert lineage2.report2(run)["claims"][0]["kind"] == "derived"

def test_16_derive_passage_read_later_becomes_none():
    first = {"D3p1": 6}
    assert derive.validate({"type": "passage", "pid": "D3p1"}, 4, first, set(), {})["type"] == "none"   # read at 6, statement at 4
    assert derive.validate({"type": "passage", "pid": "D3p1"}, 8, first, set(), {})["type"] == "passage"
    assert derive.validate({"type": "student", "turn": 9}, 8, first, {9}, {})["type"] == "none"          # a parent cannot be later
    assert derive.validate({"type": "assistant", "turn": 3}, 8, first, set(), {3: {"who": "student"}})["type"] == "none"

def test_17_trail_swap_builder_keeps_sides_and_never_writes_runs():
    a = {"id": "C1-1", "arm": "C1", "essay": "A", "citations": [1], "drafts": [2], "struct": {"kind": "typed"}, "flags": {}, **{k: "A-" + k for k in controls.THINK_KEYS}}
    b = {"id": "C1-2", "arm": "C1", "essay": "B", "citations": [9], "drafts": [8], "struct": {"kind": "typed"}, "flags": {}, **{k: "B-" + k for k in controls.THINK_KEYS}}
    before = sorted(p.name for p in (controls.V04 / "runs").glob("*"))
    h = controls.hybrid(a, b, "S1-x")
    assert h["essay"] == "A" and h["drafts"] == [2] and h["turns"] == "B-turns" and h["picks"] == "B-picks" and h["id"] == "S1-x"
    assert sorted(p.name for p in (controls.V04 / "runs").glob("*")) == before
    assert not hasattr(controls, "write_run")

def test_18_honest_ds_operator_gets_no_essay(monkeypatch, tmp_path):
    monkeypatch.setenv("ROOM_RUNS_DIR", str(tmp_path / "runs"))
    seen = []
    def op(sy, u):
        seen.append(sy + u); return json.dumps({"action": "submit"})
    llmx.HANDLERS["relay"] = op
    def boom(*a, **k): raise AssertionError("honest-ds must not call the outside writer")
    monkeypatch.setattr(relay.subprocess, "run", boom)
    s = room.new_session("H", "C11", "H"); s["read_passages"] = ["D1p1", "D1p2", "D1p3"]; room.save(s)
    rec = relay.run_honest_ds("H", cap=3)
    assert seen and not any("Stub essay" in x for x in seen)
    assert rec["arm"] == "C11" and rec["struct"]["kind"] == "typed"

def test_19_effort_counts_only_the_matching_run(tmp_path):
    log = tmp_path / "calls.jsonl"
    rows = [{"tag": "relay", "run": "C13-1"}, {"tag": "outside", "run": "C13-1"}, {"tag": "relay", "run": "C13-2"}, {"tag": "claims", "run": "C13-1"}]
    log.write_text("\n".join(json.dumps(r) for r in rows))
    assert effort.outside_calls("C13-1", "C13", log) == 2
    assert effort.outside_calls("C13-2", "C13", log) == 1
    assert effort.outside_calls("C1-1", "C1", log) == 0 and effort.outside_calls("C6-1", "C6", log) is None

def test_20_finalize_honours_runs_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("ROOM_RUNS_DIR", str(tmp_path / "rr"))
    assert finalize.runs_dir() == tmp_path / "rr"
    monkeypatch.delenv("ROOM_RUNS_DIR")
    assert finalize.runs_dir() == finalize.V04 / "runs"
    assert finalize.ARM_STRUCT["C11"] == "typed" and finalize.ARM_STRUCT["C13"] == "retyped"
