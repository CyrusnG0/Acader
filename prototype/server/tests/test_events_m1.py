"""M1 event service: merge window, staging, checkpoint, submit, lease, routes."""
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.events_service import Conflict, EventService, Invalid, LogNotFound
from app.main import create_app
from engine.events import (canonical_json, count_words, floor_window, sha256_hex, ts_seconds,
                           ts_window)

T0 = datetime(2026, 11, 2, 14, 0, 0, tzinfo=timezone.utc)
DOC = {"type": "doc", "content": [{"type": "paragraph",
                                   "content": [{"type": "text", "text": "Some words here"}]}]}
EMPTY = {"type": "doc", "content": [{"type": "paragraph"}]}


def h(doc):
    return sha256_hex(canonical_json(doc))


def step(word="word"):
    return {"stepType": "replace", "from": 1, "to": 1,
            "slice": {"content": [{"type": "text", "text": word}]}}


class Clock:
    def __init__(self, t):
        self.t = t

    def __call__(self):
        return self.t

    def advance(self, **kw):
        self.t += timedelta(**kw)


class Rig:
    """One log, one lease, continuous revs; works on a service or through the API."""

    def __init__(self, svc, clock, log_id="log1"):
        self.svc, self.clock, self.log_id = svc, clock, log_id
        svc.open_log(log_id, assignment_id="a1", consent_version=1, mapper_enabled=False)
        self.token = svc.acquire_lease(log_id, device_id="dev1")["token"]
        self.seq = 0
        self.rev = 0

    def hb(self):
        # the same device re-acquires, as a client does after a long pause
        self.token = self.svc.acquire_lease(self.log_id, device_id="dev1")["token"]

    def batch(self, n=1, kind=None):
        self.hb()
        self.seq += 1
        base = self.rev
        self.rev += n
        return self.svc.ack_batch(self.log_id, client_seq=self.seq, base_rev=base,
                                  doc_rev=self.rev, steps=[step() for _ in range(n)],
                                  input_kind=kind if kind is not None else {"keyboard": n},
                                  lease_token=self.token)

    def types(self):
        return [e["type"] for e in self.svc.events(self.log_id)]

    def batches(self):
        return [e for e in self.svc.events(self.log_id) if e["type"] == "editor.batch"]


@pytest.fixture
def clock():
    return Clock(T0)


@pytest.fixture
def svc(clock):
    return EventService(":memory:", clock)


@pytest.fixture
def rig(svc, clock):
    return Rig(svc, clock)


def api(tmp_path=None, clock=None):
    path = str(tmp_path / "r.db") if tmp_path else ":memory:"
    app = create_app(path, clock)
    return TestClient(app), app.state.events


def new_api_log(client, clock):
    client.post("/logs", json={"log_id": "L", "assignment_id": "a", "consent_version": 1,
                               "mapper_enabled": False})
    tok = client.post("/logs/L/lease", json={"device_id": "d"}).json()["token"]
    return tok


def api_batch(client, tok, seq, base, n=1, **extra):
    body = {"client_seq": seq, "base_rev": base, "doc_rev": base + n,
            "steps": [step() for _ in range(n)], "input_kind": {"keyboard": n},
            "lease_token": tok}
    body.update(extra)
    return client.post("/logs/L/batches", json=body)


def api_submit(client, tok, key="key-12345", rev=1, doc=DOC):
    return client.post("/logs/L/submit", json={"idempotency_key": key, "doc_rev": rev,
                                               "doc_hash": h(doc), "snapshot": doc,
                                               "lease_token": tok})


# ---- a. merge window ---------------------------------------------------------------------

def test_merge_window_boundaries(rig, clock):
    rig.batch(1, {"keyboard": 3})
    clock.advance(minutes=2, seconds=30)
    rig.batch(2, {"keyboard": 1, "ime": 4})
    clock.t = T0 + timedelta(minutes=4, seconds=59, milliseconds=999)
    rig.batch(1, {"dictation": 2})
    rev3 = rig.rev
    assert rig.batches() == []
    clock.t = T0 + timedelta(minutes=5)
    rig.batch(1, {"keyboard": 1})
    bs = rig.batches()
    assert len(bs) == 1
    b = bs[0]
    assert b["ts"] == "2026-11-02T14:00:00Z"
    assert b["payload"]["steps"] == [step()] * 4
    assert b["payload"]["input_kind"] == {"keyboard": 4, "ime": 4, "dictation": 2,
                                          "replacement": 0}
    assert set(b["payload"]) == {"steps", "input_kind"}
    assert b["doc_rev"] == rev3
    assert b["client_seq"] is None
    clock.t = T0 + timedelta(minutes=7, seconds=41)
    rig.batch(1)
    clock.advance(minutes=5)
    rig.batch(1)
    assert [e["ts"] for e in rig.batches()] == ["2026-11-02T14:00:00Z", "2026-11-02T14:05:00Z"]


def test_gap_across_windows_one_event_per_active_window(rig, clock):
    clock.t = T0 + timedelta(minutes=1)
    rig.batch()
    clock.t = T0 + timedelta(minutes=23)
    rig.batch()
    clock.t = T0 + timedelta(minutes=40)
    assert rig.svc.flush_due() == 1
    assert [e["ts"] for e in rig.batches()] == ["2026-11-02T14:00:00Z", "2026-11-02T14:20:00Z"]


# ---- b. units -----------------------------------------------------------------------------

def test_floor_window_units():
    def u(*a, **k):
        return datetime(2026, 1, 1, *a, tzinfo=k.get("tz", timezone.utc))
    assert ts_window(u(14, 4, 59)) == "2026-01-01T14:00:00Z"
    assert ts_window(u(14, 5, 0)) == "2026-01-01T14:05:00Z"
    assert ts_window(u(23, 59, 59)) == "2026-01-01T23:55:00Z"
    plus2 = timezone(timedelta(hours=2))
    assert ts_window(u(16, 7, 0, tz=plus2)) == "2026-01-01T14:05:00Z"
    assert floor_window(u(14, 4, 59)).tzinfo is not None
    assert ts_seconds(datetime(2026, 1, 1, 1, 2, 3, 999999, tzinfo=timezone.utc)) \
        == "2026-01-01T01:02:03Z"
    with pytest.raises(ValueError):
        floor_window(datetime(2026, 1, 1, 14, 0))
    with pytest.raises(ValueError):
        ts_seconds(datetime(2026, 1, 1, 14, 0))


def test_count_words_units():
    two = {"type": "doc", "content": [
        {"type": "paragraph", "content": [{"type": "text", "text": "one two"}]},
        {"type": "paragraph", "content": [{"type": "text", "text": "three"}]}]}
    assert count_words(two) == 3
    glued = {"type": "doc", "content": [
        {"type": "paragraph", "content": [{"type": "text", "text": "a"}]},
        {"type": "paragraph", "content": [{"type": "text", "text": "b"}]}]}
    assert count_words(glued) == 2
    br = {"type": "doc", "content": [{"type": "paragraph", "content": [
        {"type": "text", "text": "a"}, {"type": "hard_break"}, {"type": "text", "text": "b"}]}]}
    assert count_words(br) == 2
    marks = {"type": "doc", "content": [{"type": "paragraph", "content": [
        {"type": "text", "text": "wo"}, {"type": "text", "text": "rd", "marks": []}]}]}
    assert count_words(marks) == 1
    assert count_words(EMPTY) == 0
    assert count_words({"type": "doc"}) == 0


# ---- c. no per-burst activity -------------------------------------------------------------

def test_twenty_batches_one_event_and_round_timestamps(rig, clock):
    for i in range(20):
        clock.advance(seconds=7)
        rig.batch()
    clock.t = T0 + timedelta(minutes=10, seconds=13)
    rig.batch()
    bs = rig.batches()
    assert len(bs) == 1 and len(bs[0]["payload"]["steps"]) == 20
    rig.hb()
    rig.svc.checkpoint(rig.log_id, doc_rev=rig.rev, doc_hash=h(DOC), snapshot=DOC,
                       lease_token=rig.token)
    for e in rig.batches():
        t = datetime.strptime(e["ts"], "%Y-%m-%dT%H:%M:%SZ")
        assert t.minute % 5 == 0 and t.second == 0


def test_staging_has_no_time_columns(svc):
    cols = [r[1] for r in svc.db.execute("PRAGMA table_info(staging)")]
    assert cols == ["id", "log_id", "client_seq", "win", "base_rev", "doc_rev", "body"]


def test_staging_stores_only_window(rig, clock):
    clock.advance(minutes=1, seconds=23)
    rig.batch()
    rows = rig.svc.db.execute("SELECT win, body FROM staging").fetchall()
    assert rows[0][0] == "2026-11-02T14:00:00Z"
    assert "14:01:23" not in rows[0][1]


@pytest.mark.parametrize("field", ["ts", "typed_at", "client_ts"])
def test_client_timing_field_rejected(clock, field):
    client, _ = api(clock=clock)
    tok = new_api_log(client, clock)
    r = api_batch(client, tok, 1, 0, **{field: "2026-11-02T14:00:01Z"})
    assert r.status_code == 422


# ---- d. restart safety --------------------------------------------------------------------

def test_restart_keeps_staged_rows(tmp_path, clock):
    path = str(tmp_path / "e.db")
    s1 = EventService(path, clock)
    r = Rig(s1, clock)
    for _ in range(3):
        r.batch()
    s1.store.close()
    s2 = EventService(path, clock)
    assert s2.db.execute("SELECT COUNT(*) FROM staging").fetchone()[0] == 3
    assert s2.store.head("log1")["type"] == "log.open"
    tok = s2.acquire_lease("log1", device_id="dev1")["token"]
    s2.checkpoint("log1", doc_rev=3, doc_hash=h(DOC), snapshot=DOC, lease_token=tok)
    types = [e["type"] for e in s2.events("log1")]
    assert types == ["log.open", "editor.batch", "doc.checkpoint"]
    assert len(s2.events("log1")[1]["payload"]["steps"]) == 3
    s2.close()
    s3 = EventService(path, clock)
    assert s3.flush_due() == 0
    clock.advance(minutes=30)
    assert s3.flush_due() == 0
    assert [e["type"] for e in s3.events("log1")].count("editor.batch") == 1
    tok = s3.acquire_lease("log1", device_id="dev1")["token"]
    before = len(s3.events("log1"))
    res = s3.ack_batch("log1", client_seq=2, base_rev=1, doc_rev=2, steps=[step()],
                       input_kind={}, lease_token=tok)
    assert res["duplicate"] is True and res["doc_rev"] == 3
    assert len(s3.events("log1")) == before
    assert s3.db.execute("SELECT COUNT(*) FROM staging").fetchone()[0] == 0


# ---- e. flush_due -------------------------------------------------------------------------

def test_flush_due(rig, clock):
    rig.batch()
    assert rig.svc.flush_due() == 0
    clock.advance(minutes=5)
    assert rig.svc.flush_due() == 1
    assert len(rig.batches()) == 1
    assert rig.svc.flush_due() == 0
    assert len(rig.batches()) == 1


# ---- f. checkpoint ------------------------------------------------------------------------

def test_checkpoint_rules(rig, clock):
    rig.batch()
    cp = rig.svc.checkpoint(rig.log_id, doc_rev=1, doc_hash=h(DOC), snapshot=DOC,
                            lease_token=rig.token)
    assert cp["skipped"] is False
    assert rig.types() == ["log.open", "editor.batch", "doc.checkpoint"]
    p = cp["checkpoint"]["payload"]
    assert set(p) == {"doc_rev", "doc_hash", "snapshot_ref"}
    assert p["doc_hash"] == h(DOC) and p["doc_rev"] == 1 and p["snapshot_ref"].startswith("snap-")
    rig.batch()
    again = rig.svc.checkpoint(rig.log_id, doc_rev=2, doc_hash=h(DOC), snapshot=DOC,
                               lease_token=rig.token)
    assert again == {"skipped": True, "checkpoint": None}
    clock.advance(minutes=5)
    rig.hb()
    same_rev = rig.svc.checkpoint(rig.log_id, doc_rev=2, doc_hash=h(DOC), snapshot=DOC,
                                  lease_token=rig.token)
    assert same_rev["skipped"] is False
    clock.advance(minutes=5)
    rig.hb()
    no_new = rig.svc.checkpoint(rig.log_id, doc_rev=2, doc_hash=h(DOC), snapshot=DOC,
                                lease_token=rig.token)
    assert no_new["skipped"] is True
    rig.batch()
    nxt = rig.svc.checkpoint(rig.log_id, doc_rev=3, doc_hash=h(DOC), snapshot=DOC,
                             lease_token=rig.token)
    assert nxt["skipped"] is False
    assert rig.types().count("doc.checkpoint") == 3
    with pytest.raises(Conflict) as ei:
        rig.svc.checkpoint(rig.log_id, doc_rev=99, doc_hash=h(DOC), snapshot=DOC,
                           lease_token=rig.token)
    assert ei.value.code == "rev_conflict"


def test_checkpoint_flushes_pending_before_event(rig):
    rig.batch(2)
    assert rig.batches() == []
    rig.svc.checkpoint(rig.log_id, doc_rev=2, doc_hash=h(DOC), snapshot=DOC,
                       lease_token=rig.token)
    assert rig.types() == ["log.open", "editor.batch", "doc.checkpoint"]


def test_checkpoint_rev_conflict_api(clock):
    client, _ = api(clock=clock)
    tok = new_api_log(client, clock)
    api_batch(client, tok, 1, 0)
    r = client.post("/logs/L/checkpoint", json={"doc_rev": 5, "doc_hash": h(DOC),
                                                "snapshot": DOC, "lease_token": tok})
    assert r.status_code == 409 and r.json()["error"] == "rev_conflict"


# ---- g. submit ----------------------------------------------------------------------------

def test_submit_idempotent(tmp_path, clock):
    path = str(tmp_path / "s.db")
    client, svc = api(tmp_path, clock)
    tok = new_api_log(client, clock)
    assert api_batch(client, tok, 1, 0).status_code == 200
    r = api_submit(client, tok)
    assert r.status_code == 200
    body = r.json()
    evs = svc.events("L")
    assert [e["type"] for e in evs] == ["log.open", "editor.batch", "doc.checkpoint", "submit"]
    assert body["seal"] == evs[-1]["hash"] and body["seal_seq"] == evs[-1]["seq"]
    assert body["replayed"] is False and body["doc_rev"] == 1
    assert evs[-1]["payload"] == {"doc_rev": 1, "doc_hash": h(DOC), "idempotency_key": "key-12345"}
    n = len(evs)
    r2 = api_submit(client, tok)
    assert r2.status_code == 200
    assert r2.json() == {**body, "replayed": True}
    assert len(svc.events("L")) == n
    r3 = api_submit(client, tok, key="other-key-99")
    assert r3.status_code == 409 and r3.json()["error"] == "already_submitted"
    assert r3.json()["seal"] == body["seal"]
    svc.close()
    client2, svc2 = api(tmp_path, clock)
    r4 = api_submit(client2, "stale-token")
    assert r4.status_code == 200 and r4.json()["replayed"] is True
    assert r4.json()["seal"] == body["seal"]
    assert len(svc2.events("L")) == n
    _ = path


def test_empty_submit_appends_nothing(clock):
    client, svc = api(clock=clock)
    tok = new_api_log(client, clock)
    api_batch(client, tok, 1, 0)
    before = len(svc.events("L"))
    r = api_submit(client, tok, doc=EMPTY)
    assert r.status_code == 422 and r.json()["error"] == "empty_submit"
    assert len(svc.events("L")) == before
    assert svc.db.execute("SELECT COUNT(*) FROM staging").fetchone()[0] == 1


# ---- h. 409 after seal --------------------------------------------------------------------

def test_sealed_rejects_then_resubmit_reopens(clock):
    client, svc = api(clock=clock)
    tok = new_api_log(client, clock)
    api_batch(client, tok, 1, 0)
    first = api_submit(client, tok).json()
    r = api_batch(client, tok, 2, 1)
    assert r.status_code == 409 and r.json() == {"error": "sealed"}
    r = client.post("/logs/L/checkpoint", json={"doc_rev": 1, "doc_hash": h(DOC),
                                                "snapshot": DOC, "lease_token": tok})
    assert r.status_code == 409 and r.json()["error"] == "sealed"
    assert client.post("/logs/L/resubmit", json={"reason": "extension"}).status_code == 200
    assert api_batch(client, tok, 2, 1).status_code == 200
    second = api_submit(client, tok, key="key-second-1", rev=2).json()
    assert second["seal"] != first["seal"]
    assert [e["type"] for e in svc.events("L")][-3:] == ["editor.batch", "doc.checkpoint", "submit"]
    for seal in (first["seal"], second["seal"]):
        v = client.get("/logs/L/verify", params={"seal": seal}).json()
        assert v["ok"] is True, v


# ---- i. whitelist -------------------------------------------------------------------------

def sealed_client(clock):
    client, svc = api(clock=clock)
    tok = new_api_log(client, clock)
    api_batch(client, tok, 1, 0)
    api_submit(client, tok)
    return client, svc


def post_ev(client, t):
    return client.post("/logs/L/events", json={"type": t, "payload": {"x": 1}})


def test_whitelist_after_seal(clock):
    client, svc = sealed_client(clock)
    for t in ("note.add", "link.add", "record.withdrawn"):
        assert post_ev(client, t).status_code == 200
    for t in ("source.open", "card.create", "claim.edit"):
        r = post_ev(client, t)
        assert r.status_code == 409 and r.json()["error"] == "sealed"
    ev = svc.append_event("L", type="receipt.issued", actor="system", payload={"a": 1})
    assert ev["type"] == "receipt.issued"


def test_type_not_allowed(clock):
    client, _ = api(clock=clock)
    new_api_log(client, clock)
    for t in ("submit", "editor.batch", "doc.checkpoint", "log.open", "receipt.issued",
              "resubmit.open"):
        r = post_ev(client, t)
        assert r.status_code == 422 and r.json()["error"] == "type_not_allowed", t
    assert post_ev(client, "card.create").status_code == 200


def test_resubmit_unsealed(clock):
    client, _ = api(clock=clock)
    new_api_log(client, clock)
    r = client.post("/logs/L/resubmit", json={"reason": "x"})
    assert r.status_code == 409 and r.json()["error"] == "not_sealed"


# ---- j. verify ----------------------------------------------------------------------------

def test_verify_sealed_and_tamper(clock):
    client, svc = sealed_client(clock)
    seal_ev = [e for e in svc.events("L") if e["type"] == "submit"][0]
    v = client.get("/logs/L/verify").json()
    assert v["ok"] is True and v["seal_seq"] == seal_ev["seq"]
    v = client.get("/logs/L/verify", params={"seal": seal_ev["hash"]}).json()
    assert v["ok"] is True and v["seal_seq"] == seal_ev["seq"]
    post_ev(client, "note.add")
    assert client.get("/logs/L/verify").json()["ok"] is True
    bad = client.get("/logs/L/verify", params={"seal": "0" * 64}).json()
    assert bad["ok"] is False and bad["problems"]
    svc.db.execute("UPDATE events SET body = replace(body, 'word', 'WORD') WHERE type = 'editor.batch'")
    t = client.get("/logs/L/verify").json()
    assert t["ok"] is False and t["problems"]


def test_verify_unsealed(clock):
    client, _ = api(clock=clock)
    new_api_log(client, clock)
    v = client.get("/logs/L/verify").json()
    assert v["ok"] is False and v["problems"] == ["log is not sealed"] and v["seal_seq"] is None


# ---- k. lease -----------------------------------------------------------------------------

def test_lease_flow(svc, clock):
    svc.open_log("L", assignment_id="a", consent_version=1, mapper_enabled=False)
    a = svc.acquire_lease("L", device_id="A")
    assert a["doc_rev"] == 0 and a["max_client_seq"] == 0 and a["heartbeat_seconds"] == 30
    with pytest.raises(Conflict) as ei:
        svc.acquire_lease("L", device_id="B")
    assert ei.value.code == "lease_held" and ei.value.detail == {"device_id": "A"}
    clock.advance(seconds=91)
    b = svc.acquire_lease("L", device_id="B")
    with pytest.raises(Conflict) as ei:
        svc.ack_batch("L", client_seq=1, base_rev=0, doc_rev=1, steps=[step()], input_kind={},
                      lease_token=a["token"])
    assert ei.value.code == "lease_lost"
    svc.ack_batch("L", client_seq=1, base_rev=0, doc_rev=1, steps=[step()], input_kind={},
                  lease_token=b["token"])
    again = svc.acquire_lease("L", device_id="B")
    assert again["doc_rev"] == 1 and again["max_client_seq"] == 1


def test_heartbeat_keeps_lease(svc, clock):
    svc.open_log("L", assignment_id="a", consent_version=1, mapper_enabled=False)
    a = svc.acquire_lease("L", device_id="A")
    clock.advance(seconds=60)
    svc.heartbeat("L", token=a["token"])
    clock.advance(seconds=60)
    svc.ack_batch("L", client_seq=1, base_rev=0, doc_rev=1, steps=[step()], input_kind={},
                  lease_token=a["token"])
    clock.advance(seconds=91)
    with pytest.raises(Conflict) as ei:
        svc.heartbeat("L", token=a["token"])
    assert ei.value.code == "lease_lost"
    with pytest.raises(Conflict):
        svc.ack_batch("L", client_seq=2, base_rev=1, doc_rev=2, steps=[step()], input_kind={},
                      lease_token=a["token"])


def test_takeover(svc):
    svc.open_log("L", assignment_id="a", consent_version=1, mapper_enabled=False)
    a = svc.acquire_lease("L", device_id="A")
    b = svc.acquire_lease("L", device_id="B", takeover=True)
    assert b["token"] != a["token"]
    with pytest.raises(Conflict) as ei:
        svc.heartbeat("L", token=a["token"])
    assert ei.value.code == "lease_lost"
    same = svc.acquire_lease("L", device_id="B")
    assert same["token"] != b["token"]


# ---- l. validation ------------------------------------------------------------------------

def test_float_rejected(clock):
    client, svc = api(clock=clock)
    tok = new_api_log(client, clock)
    r = client.post("/logs/L/batches", json={
        "client_seq": 1, "base_rev": 0, "doc_rev": 1, "lease_token": tok,
        "steps": [{"stepType": "replace", "from": 1.5, "to": 1}], "input_kind": {}})
    assert r.status_code == 422 and r.json()["error"] == "not_canonical"
    assert svc.db.execute("SELECT COUNT(*) FROM staging").fetchone()[0] == 0
    assert svc._state("L") == (0, 0)


def test_stale_client_seq_and_revs(rig):
    rig.batch()
    rig.batch()
    with pytest.raises(Conflict) as ei:
        rig.svc.ack_batch(rig.log_id, client_seq=1, base_rev=2, doc_rev=3, steps=[step()],
                          input_kind={}, lease_token=rig.token)
    assert ei.value.code == "stale_client_seq" and ei.value.detail == {"max_client_seq": 2}
    with pytest.raises(Invalid) as ei:
        rig.svc.ack_batch(rig.log_id, client_seq=3, base_rev=2, doc_rev=9, steps=[step()],
                          input_kind={}, lease_token=rig.token)
    assert ei.value.code == "bad_batch"
    with pytest.raises(Conflict) as ei:
        rig.svc.ack_batch(rig.log_id, client_seq=3, base_rev=7, doc_rev=8, steps=[step()],
                          input_kind={}, lease_token=rig.token)
    assert ei.value.code == "rev_conflict" and ei.value.detail == {"doc_rev": 2}
    with pytest.raises(Invalid):
        rig.svc.ack_batch(rig.log_id, client_seq=3, base_rev=2, doc_rev=3, steps=[step()],
                          input_kind={"mouse": 1}, lease_token=rig.token)
    with pytest.raises(Invalid):
        rig.svc.ack_batch(rig.log_id, client_seq=3, base_rev=2, doc_rev=2, steps=[],
                          input_kind={}, lease_token=rig.token)
    dup = rig.svc.ack_batch(rig.log_id, client_seq=2, base_rev=1, doc_rev=2, steps=[step()],
                            input_kind={}, lease_token=rig.token)
    assert dup["duplicate"] is True


# ---- m. unknown log -----------------------------------------------------------------------

def test_unknown_log_404(clock):
    client, svc = api(clock=clock)
    assert client.get("/logs/nope/events").status_code == 404
    assert client.get("/logs/nope/verify").status_code == 404
    assert client.post("/logs/nope/lease", json={"device_id": "d"}).status_code == 404
    assert client.post("/logs/nope/events", json={"type": "note.add", "payload": {}}
                       ).json() == {"error": "not_found"}
    with pytest.raises(LogNotFound):
        svc.events("nope")


def test_open_log_idempotent(svc):
    a = svc.open_log("X", assignment_id="a", consent_version=1, mapper_enabled=True)
    b = svc.open_log("X", assignment_id="a", consent_version=1, mapper_enabled=True)
    assert a["event"] == b["event"] and len(svc.events("X")) == 1
    assert svc.open_log(None, assignment_id="a", consent_version=1,
                        mapper_enabled=False)["log_id"]
