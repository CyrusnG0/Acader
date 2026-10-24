"""FastAPI app for the viva runner pilot. Run: uvicorn app:app --reload (from runner/)."""
from __future__ import annotations

import json
import logging
import os
import secrets
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import viva

DATA = Path(os.environ.get("VIVA_DATA", Path(__file__).parent / "data"))
RETENTION_DAYS = 30
STATIC = Path(__file__).parent / "static"
log = logging.getLogger("viva")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

app = FastAPI(title="Viva runner (pilot)")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


def jlog(event: str, **kw):
    log.info(json.dumps({"event": event, **kw}))


# ---- storage: one JSON file per record; no database for the pilot -------------------
def _path(kind: str, rid: str) -> Path:
    if not rid.isalnum():
        raise HTTPException(404, "not found")
    return DATA / kind / f"{rid}.json"


def save(kind: str, rid: str, obj: dict):
    p = _path(kind, rid)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj))


def load(kind: str, rid: str) -> dict:
    p = _path(kind, rid)
    if not p.exists():
        raise HTTPException(404, "not found")
    return json.loads(p.read_text())


def purge_expired(now: float | None = None) -> int:
    """Delete student sessions older than RETENTION_DAYS (D-014)."""
    now = now or time.time()
    n = 0
    for p in (DATA / "sessions").glob("*.json"):
        if now - p.stat().st_mtime > RETENTION_DAYS * 86400:
            p.unlink()
            n += 1
    return n


@app.on_event("startup")
def _startup():
    n = purge_expired()
    if n:
        jlog("purged_sessions", count=n)


# ---- models ---------------------------------------------------------------------------
class NewAssignment(BaseModel):
    title: str = Field(max_length=200)
    assignment: str = Field(max_length=10_000)
    reference: str = Field(max_length=viva.MAX_CODE_CHARS)
    graph_context: str = Field("", max_length=20_000)
    raw_notes: str = Field("", max_length=20_000)
    blind: bool = False


class NewSession(BaseModel):
    assignment_id: str
    code: str
    consent_processing: bool = False   # stored + sent to the LLM provider
    consent_transcript: bool = False   # instructor may read the full answers


class Answer(BaseModel):
    text: str = Field("", max_length=5_000)
    seconds: float = 0


class Answers(BaseModel):
    token: str
    answers: list[Answer]


class Rating(BaseModel):
    token: str
    winner: str  # "X" | "Y" | "tie"


def _check(token: str, expected: str):
    if not secrets.compare_digest(token or "", expected):
        raise HTTPException(403, "bad token")


# ---- instructor ------------------------------------------------------------------------
@app.post("/api/assignments")
def create_assignment(a: NewAssignment):
    rid, token = secrets.token_hex(6), secrets.token_urlsafe(16)
    save("assignments", rid, {**a.model_dump(), "instructor_token": token, "created": time.time()})
    jlog("assignment_created", id=rid, blind=a.blind)
    return {"id": rid, "student_link": f"/s/{rid}", "instructor_token": token,
            "instructor_link": f"/i/{rid}?token={token}"}


@app.get("/api/assignments/{aid}/public")
def public_assignment(aid: str):
    a = load("assignments", aid)
    return {"title": a["title"], "assignment": a["assignment"]}


# ---- student ---------------------------------------------------------------------------
@app.post("/api/sessions")
def create_session(s: NewSession):
    if not s.consent_processing:
        raise HTTPException(400, "consent to processing is required; otherwise use the instructor's normal route")
    a = load("assignments", s.assignment_id)
    sid, stoken = secrets.token_hex(6), secrets.token_urlsafe(16)
    ctx = lambda event, **kw: jlog(event, session=sid, **kw)  # noqa: E731
    try:
        if a["blind"]:
            bs = viva.generate_blind(a["assignment"], a["reference"], s.code,
                                     a["graph_context"], a["raw_notes"], log=ctx)
            sets = {k: [q.__dict__ for q in v] for k, v in bs.questions.items()}
            shown = sets["X"]  # student answers set X; instructor rates X vs Y quality
            rec_blind = {"labels": bs.labels, "sets": sets, "rating": None}
        else:
            qs = viva.generate_questions(a["assignment"], a["reference"], s.code, a["graph_context"], log=ctx)
            shown, rec_blind = [q.__dict__ for q in qs], None
    except viva.GenerationError as e:
        jlog("session_failed", session=sid, kind=type(e).__name__)
        return JSONResponse(status_code=502, content={
            "error": "generation_failed", "kind": type(e).__name__,
            "message": "Question generation failed. Please tell your instructor; they can run the viva by hand."})
    save("sessions", sid, {"assignment_id": s.assignment_id, "code": s.code, "questions": shown,
                           "blind": rec_blind, "answers": None, "student_token": stoken,
                           "consent_transcript": s.consent_transcript, "created": time.time()})
    jlog("session_created", session=sid, assignment=s.assignment_id, n=len(shown))
    return {"session_id": sid, "token": stoken, "questions": shown}


@app.post("/api/sessions/{sid}/answers")
def submit_answers(sid: str, body: Answers):
    s = load("sessions", sid)
    _check(body.token, s["student_token"])
    if len(body.answers) != len(s["questions"]):
        raise HTTPException(400, "answer count must match question count")
    s["answers"] = [a.model_dump() for a in body.answers]
    save("sessions", sid, s)
    return {"ok": True}


@app.get("/api/sessions/{sid}/export")
def export_session(sid: str, token: str):
    s = load("sessions", sid)
    _check(token, s["student_token"])
    return {k: s[k] for k in ("code", "questions", "answers", "created")}


@app.delete("/api/sessions/{sid}")
def delete_session(sid: str, token: str):
    s = load("sessions", sid)
    _check(token, s["student_token"])
    _path("sessions", sid).unlink()
    jlog("session_deleted", session=sid)
    return {"ok": True}


# ---- instructor reports ----------------------------------------------------------------
def _signals(s: dict) -> dict:
    ans = s["answers"] or []
    return {"questions": len(s["questions"]),
            "answered": sum(1 for a in ans if a["text"].strip()),
            "avg_answer_chars": round(sum(len(a["text"]) for a in ans) / len(ans)) if ans else 0,
            "total_seconds": round(sum(a["seconds"] for a in ans))}


@app.get("/api/assignments/{aid}/report")
def report(aid: str, token: str):
    a = load("assignments", aid)
    _check(token, a["instructor_token"])
    rows = []
    for p in sorted((DATA / "sessions").glob("*.json")):
        s = json.loads(p.read_text())
        if s["assignment_id"] != aid:
            continue
        row = {"session_id": p.stem, "signals": _signals(s), "questions": s["questions"],
               "blind_set_Y": s["blind"]["sets"]["Y"] if s["blind"] else None,
               "rated": bool(s["blind"] and s["blind"]["rating"])}
        # transcript only with the student's consent (D-014)
        row["answers"] = s["answers"] if s["consent_transcript"] else None
        row["transcript_shared"] = s["consent_transcript"]
        rows.append(row)
    return {"title": a["title"], "sessions": rows,
            "note": "Signals describe the session. They are not a verdict; you decide any follow-up."}


@app.post("/api/sessions/{sid}/rate")
def rate(sid: str, body: Rating):
    s = load("sessions", sid)
    a = load("assignments", s["assignment_id"])
    _check(body.token, a["instructor_token"])
    if not s["blind"]:
        raise HTTPException(400, "not a blind session")
    if body.winner not in ("X", "Y", "tie"):
        raise HTTPException(400, "winner must be X, Y or tie")
    s["blind"]["rating"] = body.winner
    save("sessions", sid, s)
    return {"ok": True}


@app.get("/api/assignments/{aid}/blind-summary")
def blind_summary(aid: str, token: str):
    a = load("assignments", aid)
    _check(token, a["instructor_token"])
    tally = {"graph": 0, "raw": 0, "tie": 0, "unrated": 0}
    for p in (DATA / "sessions").glob("*.json"):
        s = json.loads(p.read_text())
        if s["assignment_id"] != aid or not s["blind"]:
            continue
        r = s["blind"]["rating"]
        if r is None:
            tally["unrated"] += 1
        elif r == "tie":
            tally["tie"] += 1
        else:
            tally[s["blind"]["labels"][r]] += 1
    rated = tally["graph"] + tally["raw"] + tally["tie"]
    return {**tally, "rated": rated, "rule": "graph needs >= 6 of 10 rated sessions; otherwise drop premise 3",
            "graph_passes": tally["graph"] >= 6}


# ---- pages -----------------------------------------------------------------------------
@app.get("/")
def instructor_new():
    return FileResponse(STATIC / "instructor.html")


@app.get("/i/{aid}")
def instructor_view(aid: str):
    return FileResponse(STATIC / "report.html")


@app.get("/s/{aid}")
def student_page(aid: str):
    return FileResponse(STATIC / "student.html")
