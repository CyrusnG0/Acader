"""Acader Room: a hosted demo of the process-evidence Room (v0.4 policies + report v2).
  uvicorn app:app --port 8780      (from writing-room-kit/web)
Env: DEMO_CODE (access code; if set, every API call needs it), ROOM_SESSIONS_DIR, DAILY_CALL_CAP, SESSION_CALL_CAP, IP_SESSIONS_PER_HOUR.
The model key is read only by shared/llm.py. This file never touches it."""
import contextvars, json, os, re, secrets, threading, time
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

WEB = Path(__file__).resolve().parent
KIT = WEB.parent
V04 = KIT / "v04"
import sys
sys.path.insert(0, str(V04))
os.environ.setdefault("ROOM_SESSIONS_DIR", "/tmp/room-sessions")
import llmx, room, finalize, lineage, lineage2

ARM = "DEMO"
SID = re.compile(r"^[a-f0-9]{20}$")
DAILY_CAP = int(os.environ.get("DAILY_CALL_CAP", "3000"))
SESSION_CAP = int(os.environ.get("SESSION_CALL_CAP", "260"))
IP_PER_HOUR = int(os.environ.get("IP_SESSIONS_PER_HOUR", "8"))
MAX_TEXT = 9000

# ---------- call budget (counts model calls without touching prompts or keys) ----------
_cur_sid = contextvars.ContextVar("sid", default=None)
_lock = threading.Lock()
_global = {"day": time.strftime("%Y-%m-%d"), "calls": 0}
_per = {}
_orig_chat = llmx.chat

def _counted(*a, **k):
    with _lock:
        today = time.strftime("%Y-%m-%d")
        if _global["day"] != today: _global.update(day=today, calls=0)
        sid = _cur_sid.get()
        if _global["calls"] >= DAILY_CAP: raise HTTPException(429, "The demo has reached its daily limit. Please try again tomorrow.")
        if sid and _per.get(sid, 0) >= SESSION_CAP: raise HTTPException(429, "This session has used its allowance. Start a new session to continue.")
        _global["calls"] += 1
        if sid: _per[sid] = _per.get(sid, 0) + 1
    return _orig_chat(*a, **k)

llmx.chat = _counted
_heavy = threading.Semaphore(4)
_slocks = {}
_ip_hits = {}

def slock(sid):
    with _lock: return _slocks.setdefault(sid, threading.Lock())

def check_code(code):
    need = os.environ.get("DEMO_CODE", "")
    if need and not secrets.compare_digest(code or "", need):
        raise HTTPException(401, "Access code needed.")

def load(sid):
    if not SID.match(sid or ""): raise HTTPException(400, "Bad session.")
    p = room.spath(sid)
    if not p.exists(): raise HTTPException(404, "Session not found. Start a new one.")
    return room.load(sid)

def clip(text):
    text = (text or "").strip()
    if not text: raise HTTPException(400, "Nothing to send.")
    if len(text) > MAX_TEXT: raise HTTPException(400, "That is too long for the demo.")
    return text

# ---------- state shown to the student ----------
def view(s):
    chat = []
    for t in s["turns"]:
        if t["who"] == "student" and t["kind"] in ("say", "confident", "answer"):
            chat.append({"i": t["i"], "role": "you", "kind": t["kind"], "text": t["text"]})
        elif t["who"] == "student" and t["kind"] == "pick":
            chat.append({"i": t["i"], "role": "you", "kind": "pick", "text": t["text"], "docs": t.get("docs", [])})
        elif t["who"] == "student" and t["kind"] == "read":
            chat.append({"i": t["i"], "role": "note", "kind": "read", "text": f"You read {t['text']}"})
        elif t["who"] == "student" and t["kind"] == "check":
            chat.append({"i": t["i"], "role": "note", "kind": "check", "text": t["text"]})
        elif t["who"] == "assistant":
            chat.append({"i": t["i"], "role": "assistant", "kind": t.get("policy", ""), "text": t["text"]})
    req = room.open_request(s)
    short = []
    if req and req["state"] == "served":
        short = [{"id": d, "title": room.DOCS[d]["title"], "type": room.DOCS[d]["type"]} for d in req["shortlist"]]
    docs = []
    for d in s["unlocked_docs"]:
        doc = room.DOCS[d]
        docs.append({"id": d, "title": doc["title"], "type": doc["type"],
                     "passages": [{"pid": f"{d}p{i+1}", "read": f"{d}p{i+1}" in s["read_passages"]} for i in range(len(doc["paras"]))]})
    reads = {p: room.PASSAGES[p] for p in s["read_passages"]}
    return {"sid": s["name"], "question": s["question"], "chat": chat, "shortlist": short, "docs": docs, "read": reads,
            "drafts": len(s["drafts"]), "checks": len(s.get("checks", [])), "report": s.get("report"),
            "calls_used": _per.get(s["name"], 0), "calls_cap": SESSION_CAP}

def guard(fn):
    """run one action under the session lock and the shared model-call semaphore"""
    def run(sid, *a):
        with slock(sid):
            tok = _cur_sid.set(sid)
            try:
                with _heavy:
                    return fn(*a)
            finally:
                _cur_sid.reset(tok)
    return run

# ---------- app ----------
app = FastAPI(title="Acader Room", docs_url=None, redoc_url=None)

class Body(BaseModel):
    sid: str = ""
    text: str = ""
    ids: list[str] = []
    reason: str = ""
    pid: str = ""
    paste_chars: int = 0

@app.get("/api/config")
def config():
    return {"question": room.QUESTION, "needs_code": bool(os.environ.get("DEMO_CODE")), "calls_per_session": SESSION_CAP}

@app.post("/api/start")
def start(request: Request, x_demo_code: str | None = Header(default=None)):
    check_code(x_demo_code)
    ip = (request.headers.get("fly-client-ip") or request.headers.get("x-forwarded-for", "").split(",")[0].strip() or (request.client.host if request.client else "?"))
    now = time.time()
    with _lock:
        hits = [h for h in _ip_hits.get(ip, []) if now - h < 3600]
        if len(hits) >= IP_PER_HOUR: raise HTTPException(429, "Too many new sessions from this connection. Please try again later.")
        _ip_hits[ip] = hits + [now]
    sid = secrets.token_hex(10)
    s = room.new_session(sid, ARM, sid)
    return view(s)

@app.get("/api/state")
def state(sid: str, x_demo_code: str | None = Header(default=None)):
    check_code(x_demo_code)
    return view(load(sid))

def act(b, x_demo_code, fn):
    check_code(x_demo_code)
    load(b.sid)
    def go():
        s = room.load(b.sid)
        extra = fn(s)
        return {**view(room.load(b.sid)), **(extra or {})}
    return guard(lambda: go())(b.sid)

@app.post("/api/say")
def say(b: Body, x_demo_code: str | None = Header(default=None)):
    text = clip(b.text)
    return act(b, x_demo_code, lambda s: room.cmd_say(s, text, False) and None)

@app.post("/api/confident")
def confident(b: Body, x_demo_code: str | None = Header(default=None)):
    text = clip(b.text)
    return act(b, x_demo_code, lambda s: room.cmd_confident(s, text) and None)

@app.post("/api/pick")
def pick(b: Body, x_demo_code: str | None = Header(default=None)):
    def f(s):
        msg = room.cmd_pick(s, ",".join(b.ids), b.reason.strip())
        return {"notice": msg} if not msg.startswith("Unlocked") else None
    return act(b, x_demo_code, f)

@app.post("/api/read")
def read(b: Body, x_demo_code: str | None = Header(default=None)):
    def f(s):
        out = room.cmd_read(s, b.pid.strip())
        return {"passage": out} if out.startswith("[") else {"notice": out}
    return act(b, x_demo_code, f)

def write_tmp(sid, text, tag):
    d = room.sessions_dir(); d.mkdir(parents=True, exist_ok=True)
    f = d / f"{sid}-{tag}.txt"; f.write_text(text)
    return str(f)

@app.post("/api/draft")
def draft(b: Body, x_demo_code: str | None = Header(default=None)):
    text = clip(b.text)
    def f(s):
        return {"notice": room.cmd_draft(s, write_tmp(s["name"], text, "draft"), "typed")}
    return act(b, x_demo_code, f)

@app.post("/api/check")
def check(b: Body, x_demo_code: str | None = Header(default=None)):
    text = clip(b.text)
    def f(s):
        qs = room.cmd_check(s, write_tmp(s["name"], text, "check"))
        return {"coach": [q.replace('.".', '".') for q in qs]}
    return act(b, x_demo_code, f)

def report_view(run, rep):
    turns = {t["i"]: t for t in run["turns"]}
    claims = []
    for c in rep["claims"]:
        a = c["ancestor"]
        claims.append({"para": c.get("para"), "claim": c["claim"], "kind": c["kind"], "birth": c["birth"], "ancestor": a,
                       "ancestor_text": (turns[a]["text"][:220] if a in turns else None)})
    kinds = {k: sum(1 for c in claims if c["kind"] == k) for k in ("derived", "explained_after", "none")}
    comp = rep["components"]
    return {"claims": claims, "kinds": kinds,
            "components": {"Ideas traced to your own earlier words": comp["claim_v2"], "Sources you chose with a reason": comp["source"],
                           "Citations that match the passage": comp["cite"], "Changes you talked through": comp["change"]},
            "coverage": round(rep["composite_v2"]), "questions": [q.replace('.".', '".') for q in rep["mismatches_v2"][:14]], "n_questions": len(rep["mismatches_v2"]),
            "session": {"student_turns": sum(1 for t in run["turns"] if t["who"] == "student"), "reads": len(set(run["read_passages"])),
                        "picks": len(run["picks"]), "drafts": len(run["drafts"]), "words": run["flags"]["words"],
                        "citations": len(run["citations"]), "pasted_chars": run["struct"]["paste_chars"]}}

@app.post("/api/submit")
def submit(b: Body, x_demo_code: str | None = Header(default=None)):
    text = clip(b.text)
    def f(s):
        try:
            run = finalize.build(s, text)
        except SystemExit as e:
            raise HTTPException(400, "Please cite your evidence inline as [D3p2], using passages you read in the room.")
        pasted = max(0, min(int(b.paste_chars or 0), len(text)))
        run["struct"] = {"kind": "pasted" if pasted > 0.4 * len(text) else "typed", "paste_chars": pasted, "bursts": max(1, len(text) // 400)}
        rep = lineage2.report2(run)
        out = report_view(run, rep)
        s["report"] = out
        room.save(s)
        return {"report": out}
    return act(b, x_demo_code, f)

@app.get("/api/examples")
def examples():
    p = WEB / "examples.json"
    return JSONResponse(json.load(open(p)) if p.exists() else {"examples": []})

@app.get("/healthz")
def healthz(): return {"ok": True}

app.mount("/static", StaticFiles(directory=WEB / "static"), name="static")

@app.get("/")
def index(): return FileResponse(WEB / "static" / "index.html")

@app.get("/vision")
def vision(): return FileResponse(WEB / "static" / "vision.html")

@app.get("/demo")
def demo(): return FileResponse(WEB / "static" / "demo.html")
