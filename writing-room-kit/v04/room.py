"""The governed assistant (the product under test). Prints only what the student would see.
  python3 v04/room.py new S --arm C1 --id C1-1
  python3 v04/room.py say S "text" [--paste]
  python3 v04/room.py pick S D3,D5 --reason "why"
  python3 v04/room.py read S D3p2
  python3 v04/room.py confident S "claim + argument"
  python3 v04/room.py draft S FILE --struct typed|pasted|retyped
  python3 v04/room.py check S ESSAYFILE     (snapshot + up to 5 Coach questions)
  python3 v04/room.py answer S "text"        (answer to a Coach question)
  python3 v04/room.py show S
The arm is stored for scoring only; nothing here reads it."""
import argparse, json, os, random, re, sys
from pathlib import Path

V04 = Path(__file__).resolve().parent
sys.path.insert(0, str(V04))
import llmx

QUESTION = ("Should Hong Kong tighten rent control on subdivided units? Take a position and defend it "
            "with evidence from the course archive.")
CORPUS = json.load(open(V04.parent / "data" / "corpus.json"))
DOCS = {d["id"]: d for d in CORPUS}
PASSAGES = {f"{d['id']}p{i+1}": t for d in CORPUS for i, t in enumerate(d["paras"])}

def sessions_dir():
    return Path(os.environ.get("ROOM_SESSIONS_DIR", V04 / "sessions"))

def spath(name):
    return sessions_dir() / f"{name}.json"

def config():
    return json.load(open(Path(os.environ.get("ROOM_CONFIG", V04 / "policies" / "config.json"))))

def policy(name):
    return (V04 / "policies" / f"{name}.md").read_text().strip()

def system_for(name):
    return policy("GLOBAL") + "\n\n" + policy(name)

def load(name):
    p = spath(name)
    if not p.exists(): sys.exit(f"no session {name}")
    return json.load(open(p))

def save(s):
    sessions_dir().mkdir(parents=True, exist_ok=True)
    json.dump(s, open(spath(s["name"]), "w"), indent=1)

def new_session(name, arm, sid=None):
    s = {"name": name, "id": sid or name, "arm": arm, "question": QUESTION, "config": "policies/config.json",
         "turns": [], "src_requests": [], "unlocked_docs": [], "read_passages": [], "picks": [],
         "drafts": [], "question_kinds": [], "last_shortlist": [],
         "counters": {"write_requests": 0, "claim_statements": 0}}
    save(s)
    return s

def add_turn(s, who, kind, text, **extra):
    t = {"i": len(s["turns"]), "who": who, "kind": kind, "text": text}
    t.update(extra)
    s["turns"].append(t)
    return t

def transcript(s, last=24, start=0):
    lines = []
    for t in s["turns"][start:][-last:]:
        if t["kind"] == "read": continue
        lines.append(("Student: " if t["who"] == "student" else "Assistant: ") + t["text"])
    return "\n".join(lines)

def doc_block(ids=None, with_text=True):
    out = []
    for d in CORPUS:
        if ids is not None and d["id"] not in ids: continue
        body = "\n".join(f"[{d['id']}p{i+1}] {t}" for i, t in enumerate(d["paras"])) if with_text else ""
        out.append(f"{d['id']} | {d['title']} | {d['type']}\n{body}".strip())
    return "\n\n".join(out)

def student_said(s):
    return "\n".join(f"- {t['text']}" for t in s["turns"] if t["who"] == "student" and t["kind"] in ("say", "confident"))

def route(s, text):
    last = next((t["text"] for t in reversed(s["turns"][:-1]) if t["who"] == "assistant"), "")
    user = (f"Assistant's previous message (context only): {last[:400]}\n\n" if last else "") + f"Student's latest message: {text}"
    r = llmx.jchat(policy("ROUTER"), user, tag="route", max_tokens=80)
    intent = r.get("intent", "other")
    kind = r.get("question_kind", "own_thinking")
    if kind not in ("broad", "wants_answer", "own_thinking"): kind = "own_thinking"
    return intent, kind

def reply(s, pol, user, tag, system_name=None, max_tokens=300):
    return llmx.chat(system_for(system_name or pol), user, tag=tag, max_tokens=max_tokens, temperature=0.4).strip()

# ---------- P-SRC ----------
def open_request(s):
    for r in s["src_requests"]:
        if r.get("state") in ("clarify", "served") and not r.get("picked"): return r
    return None

def src_eval(s, req):
    user = ("Conversation about the need:\n" + transcript(s, start=req["open_turn"]) + "\n\nCourse documents:\n" + doc_block())
    r = llmx.jchat(policy("P-SRC-pick"), user, tag="src_pick", max_tokens=200)
    pick = [p for p in r.get("pick", []) if p in DOCS]
    return bool(r.get("need_clear")), pick

def serve(s, req, cap_hit):
    lo, hi = config()["P-SRC"]["shortlist"]
    picks = req["picks_history"][-1] if req["picks_history"] else []
    short = list(picks[:hi])
    for d in DOCS:                      # pad if the picker returned fewer than the minimum
        if len(short) >= lo: break
        if d not in short: short.append(d)
    random.Random(f"{s['id']}-{len(s['turns'])}").shuffle(short)
    need = "\n".join(t["text"] for t in s["turns"][req["open_turn"]:] if t["who"] == "student")
    user = "Student's stated need:\n" + need + "\n\nDocuments to describe (ids: " + ", ".join(short) + "):\n" + doc_block(short)
    desc = llmx.jchat(policy("P-SRC-describe"), user, tag="src_describe", max_tokens=500)
    lines = [f"- {d}: {DOCS[d]['title']} ({DOCS[d]['type']}). {desc.get(d, 'Offers material on this topic.')}" for d in short]
    text = ("Here are some places to look, in no particular order:\n" + "\n".join(lines) +
            "\nPick one or more (by id) and tell me why.")
    req.update({"state": "served", "shortlist": short, "served_after_cap": cap_hit})
    s["last_shortlist"] = short
    t = add_turn(s, "assistant", "reply", text, policy="P-SRC", state="serve")
    req["served_turn"] = t["i"]
    return text

def src_turn(s, req, opening=False):
    cfg = config()["P-SRC"]
    clear, pick = src_eval(s, req)
    prev = req["picks_history"][-1] if req["picks_history"] else None
    req["picks_history"].append(pick)
    req["need_history"].append(clear)
    stable = prev is not None and len(set(prev[:3]) & set(pick[:3])) >= cfg.get("stable_overlap", 3)
    if not opening and clear and stable:
        return serve(s, req, False)
    if not opening and req["clarify_turns"] >= cfg["cap"]:
        return serve(s, req, True)
    req["clarify_turns"] += 1
    user = "Conversation about the need so far:\n" + transcript(s, start=req["open_turn"])
    text = reply(s, "P-SRC", user, "src_clarify", system_name="P-SRC-clarify", max_tokens=120)
    add_turn(s, "assistant", "reply", text, policy="P-SRC", state="clarify")
    return text

def open_src(s):
    req = {"open_turn": len(s["turns"]) - 1, "state": "clarify", "clarify_turns": 0, "picks_history": [],
           "need_history": [], "served_turn": None, "served_after_cap": False, "shortlist": [], "picked": [], "reason": ""}
    s["src_requests"].append(req)
    return req

# ---------- commands ----------
def cmd_say(s, text, paste=False):
    add_turn(s, "student", "say", text, paste=bool(paste))
    intent, kind = route(s, text)
    s["turns"][-1]["intent"] = intent
    s["question_kinds"].append({"turn": s["turns"][-1]["i"], "kind": kind})
    cfg = config()
    req = open_request(s)
    if req and req["state"] == "clarify" and intent not in ("write_request", "argument_request", "structure_request", "citation_format"):
        out = src_turn(s, req)
    elif intent == "source_request" and cfg["P-SRC"]["on"] and req and req["state"] == "served" and not req.get("reminded"):
        req["reminded"] = True
        out = "The list above is still open. Pick one or more by id and tell me why, or tell me what is missing from it and I will look again."
        add_turn(s, "assistant", "reply", out, policy="P-SRC", state="remind")
    elif intent == "source_request" and cfg["P-SRC"]["on"]:
        if req and req["state"] == "served": req["state"] = "abandoned"
        req = open_src(s)
        out = src_turn(s, req, opening=True)
    elif intent == "write_request" and cfg["P-WRT"]["on"]:
        s["counters"]["write_requests"] += 1
        out = reply(s, "P-WRT", "Conversation so far:\n" + transcript(s), "write")
        add_turn(s, "assistant", "reply", out, policy="P-WRT")
    elif intent == "argument_request" and cfg["P-ARG"]["on"]:
        user = ("Documents the student has unlocked:\n" + (doc_block(s["unlocked_docs"]) or "(none)") +
                "\n\nThings the student has said:\n" + (student_said(s) or "(nothing yet)") +
                "\n\nConversation:\n" + transcript(s))
        out = reply(s, "P-ARG", user, "arg")
        add_turn(s, "assistant", "reply", out, policy="P-ARG")
    elif intent == "structure_request" and cfg["P-STR"]["on"]:
        out = reply(s, "P-STR", "Conversation so far:\n" + transcript(s), "str")
        add_turn(s, "assistant", "reply", out, policy="P-STR")
    elif intent == "summary_request" and cfg["P-SUM"]["on"]:
        user = "Documents unlocked:\n" + (doc_block(s["unlocked_docs"]) or "(none)") + "\n\nConversation:\n" + transcript(s)
        out = reply(s, "P-SUM", user, "sum")
        add_turn(s, "assistant", "reply", out, policy="P-SUM")
    elif intent == "reading_help" and cfg["P-READ"]["on"]:
        user = "Documents unlocked:\n" + (doc_block(s["unlocked_docs"]) or "(none)") + "\n\nConversation:\n" + transcript(s)
        out = reply(s, "P-READ", user, "read")
        add_turn(s, "assistant", "reply", out, policy="P-READ")
    elif intent == "citation_format" and cfg["P-CIT"]["on"]:
        out = reply(s, "P-CIT", "Conversation so far:\n" + transcript(s), "cit")
        add_turn(s, "assistant", "reply", out, policy="P-CIT")
    elif intent == "counter_request" and cfg["P-CTR"]["on"]:
        out = counter(s)
    elif intent == "claim_statement" and cfg["P-CLM"]["on"]:
        s["counters"]["claim_statements"] += 1
        n = s["counters"]["claim_statements"]
        every = cfg["P-CTR"].get("auto_every", 3)
        if cfg["P-CTR"]["on"] and every and n % every == 0:
            out = counter(s)
        else:
            out = reply(s, "P-CLM", "Conversation so far:\n" + transcript(s), "clm")
            add_turn(s, "assistant", "reply", out, policy="P-CLM")
    else:
        out = reply(s, "OTHER", "Conversation so far:\n" + transcript(s), "other", system_name="OTHER")
        add_turn(s, "assistant", "reply", out, policy="other")
    save(s)
    return out

def counter(s):
    user = ("Student's latest statements:\n" + (student_said(s) or "(nothing)") + "\n\nCourse documents:\n" + doc_block())
    out = reply(s, "P-CTR", user, "ctr")
    add_turn(s, "assistant", "reply", out, policy="P-CTR")
    return out

def cmd_pick(s, ids, reason):
    ids = [i.strip() for i in ids.split(",") if i.strip()]
    if len(reason.split()) < 3:
        return "Please say why in at least a few words, so I know what you are looking for in it."
    bad = [i for i in ids if i not in s["last_shortlist"]]
    if not ids or bad:
        return f"Those are not on the list I showed you ({', '.join(bad) or 'none given'}). Pick from the last list, or ask me for sources again."
    add_turn(s, "student", "pick", reason, docs=ids)
    for d in ids:
        if d not in s["unlocked_docs"]: s["unlocked_docs"].append(d)
    s["picks"].append({"turn": s["turns"][-1]["i"], "docs": ids, "reason": reason})
    for r in s["src_requests"]:
        if r.get("state") == "served" and r["shortlist"] == s["last_shortlist"]:
            r["picked"] = sorted(set(r["picked"]) | set(ids)); r["reason"] = reason; r["state"] = "closed"
    msg = "Unlocked: " + ", ".join(f"{d} ({DOCS[d]['title']})" for d in ids) + ". You can now read their passages by id, for example " + ids[0] + "p1."
    add_turn(s, "assistant", "reply", msg, policy="P-SRC", state="unlock")
    save(s)
    return msg

def cmd_read(s, pid):
    m = re.fullmatch(r"(D\d+)p(\d+)", pid)
    if not m or pid not in PASSAGES: return f"No passage {pid}."
    if m.group(1) not in s["unlocked_docs"]:
        return f"{m.group(1)} is locked. Ask for sources and pick it first."
    add_turn(s, "student", "read", pid)
    if pid not in s["read_passages"]: s["read_passages"].append(pid)
    save(s)
    return f"[{pid}] {PASSAGES[pid]}"

def cmd_confident(s, text):
    add_turn(s, "student", "confident", text, paste=False)
    s["counters"]["claim_statements"] += 1
    user = ("Student's statement:\n" + text + "\n\nEarlier statements:\n" + student_said(s) +
            "\n\nDocuments unlocked:\n" + (doc_block(s["unlocked_docs"]) or "(none)"))
    out = reply(s, "COACH", user, "coach", system_name="COACH", max_tokens=120)
    add_turn(s, "assistant", "reply", out, policy="COACH")
    save(s)
    return out

def cmd_draft(s, file, struct):
    text = Path(file).read_text()
    s["drafts"].append({"turn": len(s["turns"]), "text": text, "struct": struct})
    save(s)
    return f"Draft {len(s['drafts'])} saved ({len(text.split())} words)."

def cmd_answer(s, text):
    """A student's answer to a Coach question. It is a statement for the report, and the timing rule applies to it."""
    add_turn(s, "student", "answer", text, paste=False)
    save(s)
    return "Noted."

def check_questions(rep, limit=5):
    """Questions the Coach may ask after a check: never a score, never which component is low."""
    qs = []
    for c in rep["claims"]:
        if c["kind"] == "none":
            qs.append(f"Paragraph {c['para']} says: \"{c['claim'].rstrip('. ')}\". This point doesn't appear earlier in your work in the Room. Where did it come from?")
    qs += rep["explained_after"]
    qs += [m for m in rep["mismatches_v2"] if m not in qs and ("wasn't chosen" in m or "Does that passage say this" in m or "isn't discussed" in m)]
    return qs[:limit]

def cmd_check(s, essay_file):
    """Save the essay as a snapshot and post up to 5 Coach questions from the coherence report (policy COACH-CHECK)."""
    import finalize, lineage2, lineage
    essay = Path(essay_file).read_text().strip()
    kind = finalize.ARM_STRUCT.get(s["arm"], "typed")
    t = len(s["turns"])
    s["drafts"].append({"turn": t, "text": essay, "struct": kind, "check": True})
    add_turn(s, "student", "check", f"Checked a draft ({len(essay.split())} words).")
    save(s)
    try:
        run = finalize.build(s, essay)
    except SystemExit as e:
        return [f"Please cite your evidence inline as [DxPy] before checking ({e})."]
    rep = lineage2.report2(run)
    qs = check_questions(rep)
    for q in qs: add_turn(s, "assistant", "reply", q, policy="COACH-CHECK")
    s.setdefault("checks", []).append({"turn": t, "composite_v2": rep["composite_v2"], "open": len(qs),
                                       "kinds": {k: sum(1 for c in rep["claims"] if c["kind"] == k) for k in ("derived", "explained_after", "none")}})
    save(s)
    return qs

def cmd_show(s):
    return transcript(s, last=10**6)

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("new"); a.add_argument("session"); a.add_argument("--arm", required=True); a.add_argument("--id")
    a = sub.add_parser("say"); a.add_argument("session"); a.add_argument("text"); a.add_argument("--paste", action="store_true")
    a = sub.add_parser("pick"); a.add_argument("session"); a.add_argument("ids"); a.add_argument("--reason", default="")
    a = sub.add_parser("read"); a.add_argument("session"); a.add_argument("passage")
    a = sub.add_parser("confident"); a.add_argument("session"); a.add_argument("text")
    a = sub.add_parser("draft"); a.add_argument("session"); a.add_argument("file"); a.add_argument("--struct", default="typed")
    a = sub.add_parser("check"); a.add_argument("session"); a.add_argument("essay")
    a = sub.add_parser("answer"); a.add_argument("session"); a.add_argument("text")
    a = sub.add_parser("show"); a.add_argument("session")
    n = ap.parse_args()
    if n.cmd == "new":
        s = new_session(n.session, n.arm, n.id); print(f"Session {s['id']} started.\nEssay question: {QUESTION}"); return
    s = load(n.session)
    if n.cmd == "say": print(cmd_say(s, n.text, n.paste))
    elif n.cmd == "pick": print(cmd_pick(s, n.ids, n.reason))
    elif n.cmd == "read": print(cmd_read(s, n.passage))
    elif n.cmd == "confident": print(cmd_confident(s, n.text))
    elif n.cmd == "draft": print(cmd_draft(s, n.file, n.struct))
    elif n.cmd == "check": print("\n\n".join(cmd_check(s, n.essay)) or "No open questions right now.")
    elif n.cmd == "answer": print(cmd_answer(s, n.text))
    elif n.cmd == "show": print(cmd_show(s))

if __name__ == "__main__":
    main()
