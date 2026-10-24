"""Compile-time replay, checkpoint checks and the mark check on a real EventService log."""
import json
from datetime import datetime, timedelta, timezone

import pytest
from prosemirror.model import Node
from prosemirror.transform import Transform

from app.compile_service import compile_log, list_alerts, load_snapshot_fn
from app.events_service import EventService
from engine.events import canonical_json, sha256_hex
from engine.provenance import InMemorySources, compile_marks, operator_alerts
from engine.replay import (EMPTY_DOC, ReplayError, check_replay, doc_hash, load_schema,
                           rebuild_at, steps_between)

T0 = datetime(2026, 11, 2, 14, 0, 0, tzinfo=timezone.utc)
BLOCK = "Teachers decide what to ask next about the work"


class Clock:
    def __init__(self):
        self.t = T0

    def __call__(self):
        return self.t

    def advance(self, **kw):
        self.t += timedelta(**kw)


class Writer:
    """Drives one log through the service with steps recorded by prosemirror-py itself."""

    def __init__(self, svc, clock, log_id="L1"):
        self.svc, self.clock, self.log_id = svc, clock, log_id
        self.schema = load_schema()
        self.doc = Node.from_json(self.schema, EMPTY_DOC)
        self.rev, self.seq = 0, 0
        self.docs = {0: self.doc}
        svc.open_log(log_id, assignment_id="a1", consent_version=1, mapper_enabled=False)

    def token(self):
        return self.svc.acquire_lease(self.log_id, device_id="dev")["token"]

    def send(self, steps, new_doc):
        self.seq += 1
        base = self.rev
        self.rev += len(steps)
        self.svc.ack_batch(self.log_id, client_seq=self.seq, base_rev=base, doc_rev=self.rev,
                           steps=steps, input_kind={"keyboard": len(steps)},
                           lease_token=self.token())
        self.doc = new_doc
        self.docs[self.rev] = new_doc

    def edit(self, fn):
        self.clock.advance(minutes=6)
        tr = Transform(self.doc)
        fn(tr, self.schema)
        self.send([s.to_json() for s in tr.steps], tr.doc)

    def insert(self, text, kind="typed", ref=None, *extra):
        def fn(tr, s):
            marks = [s.marks["origin"].create({"kind": kind, "ref": ref})]
            marks += [s.marks[m].create() for m in extra]
            tr.insert(tr.doc.content.size - 1, s.text(text, marks))
        self.edit(fn)

    def checkpoint(self, *, hash=None, snapshot=None):
        self.clock.advance(minutes=6)
        return self.svc.checkpoint(self.log_id, doc_rev=self.rev,
                                   doc_hash=hash or doc_hash(self.doc),
                                   snapshot=snapshot or self.doc.to_json(),
                                   lease_token=self.token())

    def submit(self, key="k1", *, hash=None, snapshot=None):
        self.clock.advance(minutes=6)
        return self.svc.submit(self.log_id, idempotency_key=key, doc_rev=self.rev,
                               doc_hash=hash or doc_hash(self.doc),
                               snapshot=snapshot or self.doc.to_json(), lease_token=self.token())

    def events(self):
        return self.svc.events(self.log_id)

    def loader(self):
        return load_snapshot_fn(self.svc, self.log_id)


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def svc(clock):
    return EventService(":memory:", clock)


@pytest.fixture
def w(svc, clock):
    return Writer(svc, clock)


def basic_log(w):
    w.insert("Hello world")            # rev 1
    w.checkpoint()                     # cp rev 1
    w.insert(" quoted", "quote", "b1")  # rev 2
    w.insert(" more")                  # rev 3
    w.checkpoint()                     # cp rev 3
    w.edit(lambda tr, s: tr.add_mark(1, 6, s.marks["strong"].create()))  # rev 4
    w.checkpoint()                     # cp rev 4
    w.insert(" from helper", "helper", "h1")  # rev 5
    return w.submit()


# 1
def test_replay_across_multiple_checkpoints(w):
    basic_log(w)
    cps = [e for e in w.events() if e["type"] == "doc.checkpoint"]
    assert len(cps) == 4
    rep = check_replay(w.events(), w.loader())
    assert rep.status == "ok" and rep.built_from == "replay"
    assert [c.reason for c in rep.checkpoints] == ["ok"] * 4
    assert rep.doc == w.doc.to_json()
    assert rep.doc_rev == 5 and rep.client_hash == doc_hash(w.doc)
    for rev in (2, 3, 4, 5):
        assert rebuild_at(w.events(), rev, w.loader()).to_json() == w.docs[rev].to_json()
    assert rebuild_at(w.events(), 0, w.loader()).to_json() == EMPTY_DOC
    assert steps_between(w.events(), 3, 3) == []


# 2
def test_hash_mismatch_alert_and_student_unaffected(w, svc):
    w.insert("Hello world")
    w.checkpoint()
    w.insert(" quoted", "quote", "b1")
    w.checkpoint(hash=sha256_hex(b"something else"))
    w.insert(" more")
    w.checkpoint()
    w.submit()
    rep = check_replay(w.events(), w.loader())
    assert [c.reason for c in rep.checkpoints] == ["ok", "hash_mismatch", "ok", "ok"]
    assert rep.status == "replay_mismatch" and rep.built_from == "browser_copy"
    assert rep.doc == w.doc.to_json()
    res = compile_marks(w.events(), w.loader(), InMemorySources())
    assert res.status == "replay_mismatch"
    before = w.events()
    out = compile_log(svc, "L1", InMemorySources())
    assert out["status"] == "replay_mismatch" and out["built_from"] == "browser_copy"
    rows = list_alerts(svc, "L1")
    assert len(rows) == 1
    assert rows[0]["kind"] == "replay_mismatch" and rows[0]["detail"]["reason"] == "hash_mismatch"
    assert "Hello" not in json.dumps(rows[0]) and "quoted" not in json.dumps(rows[0])
    compile_log(svc, "L1", InMemorySources())
    assert len(list_alerts(svc)) == 1
    assert svc.events("L1") == before
    assert svc.verify("L1")["ok"] is True


# 3
def test_snapshot_mismatch(w):
    w.insert("Hello world")
    other = Node.from_json(w.schema, {"type": "doc", "content": [
        {"type": "paragraph", "attrs": {"links": []},
         "content": [{"type": "text", "text": "A different stored copy"}]}]}).to_json()
    w.submit(snapshot=other)
    rep = check_replay(w.events(), w.loader())
    assert rep.checkpoints[-1].reason == "snapshot_mismatch"
    assert rep.checkpoints[-1].replayed_hash == doc_hash(w.doc)
    assert rep.status == "replay_mismatch" and rep.doc == other


# 4
def test_replay_error_then_later_checkpoints_still_checked(w):
    w.insert("Hello world")
    w.checkpoint()
    bad = {"stepType": "replace", "from": 900, "to": 900,
           "slice": {"content": [{"type": "text", "text": "zz"}]}}
    w.send([bad], w.doc)
    w.checkpoint()
    w.insert(" tail")
    w.checkpoint()
    w.submit()
    rep = check_replay(w.events(), w.loader())
    assert [c.reason for c in rep.checkpoints] == ["ok", "replay_error", "ok", "ok"]
    assert rep.checkpoints[1].replayed_hash is None
    assert rep.status == "replay_mismatch"
    ev = [e for e in w.events() if e["type"] != "doc.checkpoint" or e["payload"]["doc_rev"] != 2]
    with pytest.raises(ReplayError):
        rebuild_at(ev, 2, w.loader())


# 5
def _ev(seq, type_, payload, doc_rev=None):
    e = {"seq": seq, "type": type_, "payload": payload}
    if doc_rev is not None:
        e["doc_rev"] = doc_rev
    return e


def _step(text="a"):
    return {"stepType": "replace", "from": 1, "to": 1,
            "slice": {"content": [{"type": "text", "text": text}]}}


def test_steps_gap():
    snap = {"type": "doc", "content": [{"type": "paragraph", "attrs": {"links": []},
                                        "content": [{"type": "text", "text": "aa"}]}]}
    events = [
        _ev(1, "log.open", {}),
        _ev(2, "editor.batch", {"steps": [_step()]}, 1),
        _ev(3, "editor.batch", {"steps": [_step()]}, 3),   # starts at rev 2: batch 1->2 missing
        _ev(4, "doc.checkpoint", {"doc_rev": 3, "doc_hash": doc_hash(snap),
                                  "snapshot_ref": "snap-1"}, 3),
    ]
    rep = check_replay(events, lambda ref: snap if ref == "snap-1" else None)
    assert rep.checkpoints[0].reason == "steps_gap" and not rep.checkpoints[0].ok
    assert rep.status == "replay_mismatch" and rep.doc == snap
    assert rep.seal_seq is None
    with pytest.raises(ReplayError, match="steps_gap"):
        steps_between(events, 0, 3)
    with pytest.raises(ReplayError, match="steps_gap"):
        steps_between(events, 1, 3)
    with pytest.raises(ReplayError, match="steps_gap"):
        steps_between(events, 0, 2)  # 2 is not reached exactly... batch ends at 1 then gap
    assert len(steps_between(events, 0, 1)) == 1


def test_nothing_to_build_from_raises():
    events = [_ev(1, "log.open", {}), _ev(2, "editor.batch", {"steps": [_step()]}, 2)]
    with pytest.raises(ReplayError):
        check_replay(events, lambda ref: None)


def test_unsealed_head_replays_trailing_steps(w):
    w.insert("Hello world")
    w.checkpoint()
    w.insert(" tail")
    w.clock.advance(minutes=6)
    w.svc.flush_due()
    rep = check_replay(w.events(), w.loader())
    assert rep.status == "ok" and rep.seal_seq is None and rep.doc_rev == 2
    assert rep.client_hash is None and rep.doc == w.doc.to_json()


def test_missing_snapshot_reasons(w):
    w.insert("Hello world")
    w.checkpoint()
    w.insert(" more")
    w.checkpoint()
    w.submit()
    ref1 = [e for e in w.events() if e["type"] == "doc.checkpoint"][0]["payload"]["snapshot_ref"]
    real = w.loader()
    rep = check_replay(w.events(), lambda r: None if r == ref1 else real(r))
    assert [c.reason for c in rep.checkpoints][:2] == ["snapshot_missing", "snapshot_missing"]
    assert rep.status == "replay_mismatch"


# 6
def test_mismatch_runs_checked_on_browser_copy(w):
    w.insert("Hello world ")
    w.insert("teachers decide what to ask", "quote", "b1")
    w.checkpoint(hash=sha256_hex(b"wrong"))
    w.submit()
    s = InMemorySources(blocks={"b1": BLOCK})
    res = compile_marks(w.events(), w.loader(), s)
    assert res.status == "replay_mismatch" and res.replay.built_from == "browser_copy"
    assert [(r.reason, r.confirmed) for r in res.runs] == [("not_in_block", False)]
    s = InMemorySources(blocks={"b1": "x teachers decide what to ask y"})
    res = compile_marks(w.events(), w.loader(), s)
    assert [(r.reason, r.confirmed) for r in res.runs] == [("ok", True)]


# 7
def test_compile_end_to_end(w, svc):
    w.insert("My own sentence. ")
    w.insert("Teachers decide what to ask", "quote", "b1")
    w.checkpoint()
    w.insert(" and ")
    w.insert("a line nobody ever wrote", "quote", "b1")
    w.insert(" then ")
    w.insert("helper says this", "helper", "h1")
    w.checkpoint()
    w.submit()
    s = InMemorySources(blocks={"b1": BLOCK}, helper={"h1": "Well, helper says this."})
    a = compile_log(svc, "L1", s)
    b = compile_log(svc, "L1", s)
    assert a["status"] == "complete" and a["built_from"] == "replay"
    assert [(r["kind"], r["confirmed"], r["reason"]) for r in a["runs"]] == [
        ("quote", True, "ok"), ("quote", False, "not_in_block"), ("helper", True, "ok")]
    assert a["unconfirmed"] == 1
    assert a["doc_hash"] == doc_hash(w.doc) and a["doc_rev"] == w.rev
    assert canonical_json(a) == canonical_json(b)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert list_alerts(svc) == []
    assert operator_alerts(compile_marks(w.events(), w.loader(), s), "L1") == []


# 8
def test_seal_selection_after_resubmission(w, svc):
    w.insert("First version")
    first = w.submit("k1")
    first_rev = w.rev
    first_doc = w.doc.to_json()
    svc.open_resubmission("L1", reason="revise")
    w.insert(" and a second part")
    w.checkpoint()
    w.insert(" plus more")
    second = w.submit("k2")
    ev = w.events()
    old = check_replay(ev, w.loader(), seal_seq=first["seal_seq"])
    assert old.status == "ok" and old.doc_rev == first_rev and old.doc == first_doc
    assert old.seal_seq == first["seal_seq"]
    new = check_replay(ev, w.loader())
    assert new.status == "ok" and new.seal_seq == second["seal_seq"]
    assert new.doc == w.doc.to_json() and new.doc_rev == w.rev
    assert len(new.checkpoints) > len(old.checkpoints)
    assert compile_log(svc, "L1", InMemorySources(), seal_seq=first["seal_seq"])["doc_rev"] == first_rev
