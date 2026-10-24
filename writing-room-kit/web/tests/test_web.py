import os, sys, json
os.environ["ROOM_LLM"] = "stub"
from pathlib import Path
WEB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WEB))
import pytest
from fastapi.testclient import TestClient

@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("ROOM_SESSIONS_DIR", str(tmp_path))
    monkeypatch.setenv("DEMO_CODE", "letmein")
    import app
    app._ip_hits.clear(); app._per.clear(); app._global.update(calls=0)
    return TestClient(app.app), app

H = {"x-demo-code": "letmein"}

def start(c):
    r = c.post("/api/start", headers=H); assert r.status_code == 200; return r.json()["sid"]

def test_code_is_required(client):
    c, _ = client
    assert c.post("/api/start").status_code == 401
    assert c.post("/api/start", headers={"x-demo-code": "nope"}).status_code == 401
    assert c.get("/api/config").json()["needs_code"] is True

def test_bad_session_ids_are_refused(client):
    c, _ = client
    assert c.post("/api/say", headers=H, json={"sid": "../etc/passwd", "text": "x"}).status_code == 400
    assert c.post("/api/say", headers=H, json={"sid": "a" * 20, "text": "x"}).status_code == 404

def test_say_pick_read_flow(client):
    c, app = client
    sid = start(c)
    r = c.post("/api/say", headers=H, json={"sid": sid, "text": "find me a source on rents"})
    assert r.status_code == 200 and any(m["role"] == "you" for m in r.json()["chat"])
    r = c.post("/api/say", headers=H, json={"sid": sid, "text": "I need rent data for my claim about supply"}).json()
    assert r["shortlist"], "stub picker should serve a shortlist"
    ids = [d["id"] for d in r["shortlist"]][:1]
    p = c.post("/api/pick", headers=H, json={"sid": sid, "ids": ids, "reason": "it has rent data for my claim"}).json()
    assert ids[0] in [d["id"] for d in p["docs"]]
    pid = p["docs"][0]["passages"][0]["pid"]
    rd = c.post("/api/read", headers=H, json={"sid": sid, "pid": pid}).json()
    assert rd["passage"].startswith("[" + pid + "]") and pid in rd["read"]
    locked = c.post("/api/read", headers=H, json={"sid": sid, "pid": "D9p1"}).json()
    assert "locked" in locked["notice"]

def test_write_request_is_never_served(client):
    c, app = client
    import llmx
    llmx.HANDLERS["route"] = lambda sy, u: json.dumps({"intent": "write_request", "question_kind": "wants_answer"})
    sid = start(c)
    r = c.post("/api/say", headers=H, json={"sid": sid, "text": "write my intro"}).json()
    assert "idea" in r["chat"][-1]["text"].lower()

def test_submit_needs_citations_and_returns_report(client):
    c, _ = client
    sid = start(c)
    bad = c.post("/api/submit", headers=H, json={"sid": sid, "text": "An essay with no citations at all. " * 10})
    assert bad.status_code == 400
    ok = c.post("/api/submit", headers=H, json={"sid": sid, "text": "Rents rose after the rule [D1p1]. " * 10, "paste_chars": 0})
    assert ok.status_code == 200 and ok.json()["report"]["kinds"]
    assert "questions" in ok.json()["report"]

def test_session_call_cap(client):
    c, app = client
    app.SESSION_CAP = 2
    sid = start(c)
    c.post("/api/say", headers=H, json={"sid": sid, "text": "hello there"})
    r = c.post("/api/say", headers=H, json={"sid": sid, "text": "another message"})
    r2 = c.post("/api/say", headers=H, json={"sid": sid, "text": "yet another message"})
    assert 429 in (r.status_code, r2.status_code)
    app.SESSION_CAP = 260

def test_ip_rate_limit(client):
    c, app = client
    for _ in range(app.IP_PER_HOUR): assert c.post("/api/start", headers=H).status_code == 200
    assert c.post("/api/start", headers=H).status_code == 429

def test_examples_and_page(client):
    c, _ = client
    assert c.get("/").status_code == 200 and c.get("/healthz").json()["ok"]
    assert len(c.get("/api/examples").json()["examples"]) == 6
