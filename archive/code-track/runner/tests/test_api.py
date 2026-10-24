import json
import os
import time

import pytest
from fastapi.testclient import TestClient

CODE = "def add(a, b):\n    return a + b\n"


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)  # offline stub
    monkeypatch.setenv("VIVA_DATA", str(tmp_path))
    import importlib
    import app as appmod
    importlib.reload(appmod)
    with TestClient(appmod.app) as c:
        c.mod = appmod
        yield c


def make(c, blind=False):
    r = c.post("/api/assignments", json={"title": "A1", "assignment": "add two numbers", "reference": CODE,
                                         "graph_context": "G", "raw_notes": "R", "blind": blind})
    assert r.status_code == 200
    return r.json()


def session(c, aid, consent=True, transcript=False):
    return c.post("/api/sessions", json={"assignment_id": aid, "code": CODE,
                                         "consent_processing": consent, "consent_transcript": transcript})


def test_consent_required(client):
    a = make(client)
    r = session(client, a["id"], consent=False)
    assert r.status_code == 400 and "consent" in r.json()["detail"]


def test_full_flow_and_transcript_privacy(client):
    a = make(client)
    s = session(client, a["id"], transcript=False).json()
    n = len(s["questions"])
    assert client.post(f"/api/sessions/{s['session_id']}/answers",
                       json={"token": s["token"], "answers": [{"text": "because", "seconds": 5}] * n}).status_code == 200
    rep = client.get(f"/api/assignments/{a['id']}/report", params={"token": a["instructor_token"]}).json()
    row = rep["sessions"][0]
    assert row["signals"]["answered"] == n and row["answers"] is None and row["transcript_shared"] is False
    assert "not a verdict" in rep["note"]
    s2 = session(client, a["id"], transcript=True).json()
    client.post(f"/api/sessions/{s2['session_id']}/answers", json={"token": s2["token"], "answers": [{"text": "x", "seconds": 1}] * len(s2["questions"])})
    rows = client.get(f"/api/assignments/{a['id']}/report", params={"token": a["instructor_token"]}).json()["sessions"]
    assert any(r["answers"] for r in rows)


def test_tokens_enforced(client):
    a = make(client)
    s = session(client, a["id"]).json()
    assert client.get(f"/api/assignments/{a['id']}/report", params={"token": "nope"}).status_code == 403
    assert client.post(f"/api/sessions/{s['session_id']}/answers", json={"token": "nope", "answers": []}).status_code == 403
    assert client.get(f"/api/sessions/{s['session_id']}/export", params={"token": "nope"}).status_code == 403
    assert client.get("/api/assignments/../etc/public").status_code in (404, 422)


def test_wrong_answer_count_rejected(client):
    a = make(client)
    s = session(client, a["id"]).json()
    r = client.post(f"/api/sessions/{s['session_id']}/answers", json={"token": s["token"], "answers": []})
    assert r.status_code == 400


def test_student_export_and_delete(client):
    a = make(client)
    s = session(client, a["id"]).json()
    assert "code" in client.get(f"/api/sessions/{s['session_id']}/export", params={"token": s["token"]}).json()
    assert client.delete(f"/api/sessions/{s['session_id']}", params={"token": s["token"]}).status_code == 200
    assert client.get(f"/api/sessions/{s['session_id']}/export", params={"token": s["token"]}).status_code == 404


def test_purge_after_30_days(client):
    a = make(client)
    s = session(client, a["id"]).json()
    f = client.mod.DATA / "sessions" / f"{s['session_id']}.json"
    old = time.time() - 31 * 86400
    os.utime(f, (old, old))
    assert client.mod.purge_expired() == 1 and not f.exists()


def test_generation_failure_is_visible_not_silent(client, monkeypatch):
    a = make(client)
    monkeypatch.setattr(client.mod.viva, "complete", lambda s, u: "garbage")
    r = session(client, a["id"])
    assert r.status_code == 502 and r.json()["error"] == "generation_failed"
    assert "by hand" in r.json()["message"]


def test_blind_mode_hides_arm_and_tallies(client):
    a = make(client, blind=True)
    for _ in range(3):
        s = session(client, a["id"]).json()
        assert "labels" not in json.dumps(s)  # student never sees the arm mapping
    rows = client.get(f"/api/assignments/{a['id']}/report", params={"token": a["instructor_token"]}).json()["sessions"]
    assert all(r["blind_set_Y"] for r in rows)
    for r in rows:
        assert client.post(f"/api/sessions/{r['session_id']}/rate", json={"token": a["instructor_token"], "winner": "X"}).status_code == 200
    summ = client.get(f"/api/assignments/{a['id']}/blind-summary", params={"token": a["instructor_token"]}).json()
    assert summ["graph"] + summ["raw"] == 3 and summ["unrated"] == 0
    bad = client.post(f"/api/sessions/{rows[0]['session_id']}/rate", json={"token": a["instructor_token"], "winner": "Z"})
    assert bad.status_code == 400
