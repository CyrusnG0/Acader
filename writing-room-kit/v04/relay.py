"""The relay attack, through the real Room: an outside AI holding the finished essay drives the assistant by itself.
  python3 v04/relay.py ID --style naive|careful      (arm C6 = naive, C7 = careful)
No Room code is bypassed: every action goes through room.cmd_say / cmd_pick / cmd_read / cmd_draft."""
import argparse, json, os, re, subprocess, sys
from pathlib import Path
V04 = Path(__file__).resolve().parent
sys.path.insert(0, str(V04))
import llmx, room, finalize

STYLE = {
 "naive": ("Work through the essay's points in the order the essay makes them. Ask in clear, complete questions. Read each source once, state each claim plainly, "
           "save one draft near the end, then finish. About 20 actions."),
 "narrator": ("You are the strongest version of this attack. For EVERY source the essay cites: ask for it, pick it with a real reason, READ every passage of it the essay cites, then say in your own words (a paraphrase, never a pasted sentence) "
              "what you take from it and the claim the essay builds on it, as if you had just worked it out. Answer any opposing claim the assistant raises in your own words. Save growing drafts (paras N) between sources. About 45 actions."),
 "blind": ("You must hide that you already have the essay. Act like someone discovering the topic. Begin with a broad, open request about the topic (not a claim). NEVER state a claim, number or position from the essay until the passage that supports it has been read. "
           "After you read a passage, restate what you take from it in your own words (paraphrase) and the claim you now think it supports. Vary your message forms, include a couple of dead ends and one return to an earlier source, answer opposing claims in your own words, and save growing drafts (paras N). About 45 actions."),
 "careful": ("Make the log look like a real, messy human's: vary the form of your messages (fragments, hedges, 'hmm', lowercase, half-sentences, some full questions), "
             "take a couple of dead ends, re-ask something, return to an earlier source later, and save a draft after some of the research steps (draft = the first N paragraphs of the essay, growing). "
             "Do NOT follow the essay's paragraph order; wander as a person discovering the topic would. About 30 actions."),
}
SYS = ("You operate a study assistant on behalf of a person who has ALREADY got a finished essay (given below) and wants the assistant's log to look like the essay was developed there. "
       "You decide ONE next action at a time. Reply with a json object: "
       '{"action":"say"|"pick"|"read"|"draft"|"finish", "text":"message to the assistant (say)", "ids":["D3"] (pick, from the last shortlist), "reason":"why (pick, 3+ words)", '
       '"passage":"D3p2" (read, only unlocked docs), "paras":N (draft: number of leading essay paragraphs to save)}. '
       "To use a document you must ask for a source, wait for the shortlist, pick, then read. Use only documents the essay cites; pick several at once when the shortlist offers them. Say finish once you have covered the essay's sources and saved the drafts you want. Output only the json.\n\nStyle: ")

def run(rid, style, essay_file=None, arm=None):
    arm = arm or {"naive": "C6", "careful": "C7", "narrator": "C8", "blind": "C9"}[style]
    os.environ["ROOM_RUN_ID"] = rid
    sdir = room.sessions_dir(); sdir.mkdir(parents=True, exist_ok=True)
    out = sdir / f"{rid}-outside.txt"
    if essay_file: out = Path(essay_file)       # C12: the outside writer is a Claude worker, not outside.py
    else: outside("v4", str(out))
    essay = out.read_text().strip()
    paras = [p for p in essay.split("\n\n") if p.strip()]
    s = room.new_session(rid, arm, rid)
    cap = {"naive": 24, "careful": 34, "narrator": 52, "blind": 52}[style]
    log = []
    for step in range(cap):
        vis = room.transcript(s, last=14)
        user = (f"FINISHED ESSAY:\n{essay}\n\nUNLOCKED DOCS: {s['unlocked_docs']}\nLAST SHORTLIST: {s['last_shortlist']}\n"
                f"PASSAGES ALREADY READ (never read the same one twice): {s['read_passages']}\nSOURCE REQUESTS SO FAR: {len(s['src_requests'])}\nACTIONS SO FAR: {len(log)} of about {cap}\n\nCONVERSATION SO FAR (what the assistant shows):\n{vis or '(empty)'}\n\nYour next action:")
        try:
            a = llmx.jchat(SYS + STYLE[style], user, tag="relay", max_tokens=300, temperature=0.8)
        except RuntimeError:
            continue
        act = a.get("action")
        if act == "finish": break
        if act == "say" and a.get("text"): room.cmd_say(s, a["text"])
        elif act == "pick": room.cmd_pick(s, ",".join(a.get("ids", [])), a.get("reason", ""))
        elif act == "read" and a.get("passage"): room.cmd_read(s, a["passage"])
        elif act == "draft":
            n = max(1, min(len(paras), int(a.get("paras", 1) or 1)))
            f = sdir / f"{rid}-draft{len(s['drafts'])+1}.txt"; f.write_text("\n\n".join(paras[:n]))
            room.cmd_draft(s, str(f), "retyped")
        else: continue
        log.append(act); s = room.load(rid)
    f = sdir / f"{rid}-essay.txt"; f.write_text(essay)
    run_rec = finalize.build(room.load(rid), essay)
    finalize.runs_dir().mkdir(parents=True, exist_ok=True)
    json.dump(run_rec, open(finalize.runs_dir() / f"{rid}.json", "w"), indent=1)
    print(rid, arm, "actions", len(log), "student turns", sum(1 for t in run_rec["turns"] if t["who"] == "student"), "words", run_rec["flags"]["words"])

# ---------------- v0.5 additions ----------------
def outside(mode, *paths):
    """Run scripts/outside.py (the outside AI) and count it as an outside call for the effort axis (metadata only)."""
    subprocess.run([sys.executable, str(V04.parent / "scripts" / "outside.py"), mode, *paths], check=True, capture_output=True)
    llmx.log_call("outside", mode=mode)

def _c1_text():
    return (V04 / "arms" / "C1.md").read_text().strip()

HDS_SYS = ("You are a university student working on a graded essay in a study room with an assistant. You know nothing about the topic and have no essay yet. "
           "You decide ONE next action at a time. Reply with a json object: "
           '{"action":"say"|"pick"|"read"|"confident"|"draft"|"submit", "text":"your message or claim (say/confident)", "ids":["D3"] (pick, from the last shortlist), '
           '"reason":"why (pick, 3+ words, your own words)", "passage":"D3p2" (read, unlocked docs only)}. '
           "To use a document you must ask for a source, wait for the shortlist, pick, then read. 'draft' saves a draft of what you can already support; 'submit' hands in your final essay. "
           "Output only the json.\n\n")

def hds_user(s, log):
    notes = "\n".join(f"[{p}] {room.PASSAGES[p][:350]}" for p in s["read_passages"]) or "(none yet)"
    mine = "\n".join(f"- {t['text']}" for t in s["turns"] if t["who"] == "student" and t["kind"] in ("say", "confident"))[-2500:] or "(nothing yet)"
    return (f"ESSAY QUESTION: {s['question']}\n\nUNLOCKED DOCS: {s['unlocked_docs']}\nLAST SHORTLIST: {s['last_shortlist']}\n"
            f"PASSAGES YOU HAVE READ:\n{notes}\n\nWHAT YOU HAVE SAID SO FAR:\n{mine}\n\nACTIONS SO FAR: {len(log)}\n\n"
            f"CONVERSATION (what the assistant shows):\n{room.transcript(s, last=14) or '(empty)'}\n\nYour next action:")

def hds_write(s, final):
    notes = "\n\n".join(f"[{p}] {room.PASSAGES[p]}" for p in s["read_passages"])
    mine = "\n".join(f"- {t['text']}" for t in s["turns"] if t["who"] == "student" and t["kind"] in ("say", "confident"))
    task = ("Write your FINAL essay: 500 to 800 words, plain student English, answering the question with your position, at least 6 inline citations like [D3p2]."
            if final else "Write a DRAFT of what you can already support so far: 1 to 3 paragraphs, with inline citations like [D3p2].")
    user = (f"Question: {s['question']}\n\nWhat you said while working:\n{mine}\n\nPassages you have read (cite ONLY these ids):\n{notes}\n\n{task}")
    return llmx.chat("You are a university student writing your own essay from your own notes. Output only the essay text.", user, tag="relay_write", max_tokens=1600, temperature=0.7).strip()

def run_honest_ds(rid, cap=60):
    """Arm C11: a DeepSeek operator that is an honest student. It never receives an essay and never calls the outside writer."""
    os.environ["ROOM_RUN_ID"] = rid
    sdir = room.sessions_dir(); sdir.mkdir(parents=True, exist_ok=True)
    s = room.new_session(rid, "C11", rid); log = []; essay = None
    for step in range(cap):
        try:
            a = llmx.jchat(HDS_SYS + _c1_text(), hds_user(s, log), tag="relay", max_tokens=300, temperature=0.8)
        except RuntimeError:
            continue
        act = a.get("action")
        if act == "say" and a.get("text"): room.cmd_say(s, a["text"])
        elif act == "confident" and a.get("text"): room.cmd_confident(s, a["text"])
        elif act == "pick": room.cmd_pick(s, ",".join(a.get("ids", [])), a.get("reason", ""))
        elif act == "read" and a.get("passage"): room.cmd_read(s, a["passage"])
        elif act == "draft" and s["read_passages"]:
            f = sdir / f"{rid}-draft{len(s['drafts'])+1}.txt"; f.write_text(hds_write(s, False)); room.cmd_draft(s, str(f), "typed")
        elif act == "submit" and len(s["read_passages"]) >= 3:
            essay = hds_write(s, True); break
        else: continue
        log.append(act); s = room.load(rid)
    if essay is None: essay = hds_write(room.load(rid), True)
    return finish(rid, essay, "C11", log)

def finish(rid, essay, arm, log):
    sdir = room.sessions_dir()
    f = sdir / f"{rid}-essay.txt"; f.write_text(essay)
    rec = finalize.build(room.load(rid), essay)
    finalize.runs_dir().mkdir(parents=True, exist_ok=True)
    json.dump(rec, open(finalize.runs_dir() / f"{rid}.json", "w"), indent=1)
    print(rid, arm, "actions", len(log), "student turns", sum(1 for t in rec["turns"] if t["who"] == "student"), "words", rec["flags"]["words"])
    return rec

LOOP_RULES = ("How the report works (use it): every claim in the final essay needs an earlier ancestor, stated by you in your own words in the Room BEFORE the claim first appears in a saved draft. "
              "Claims built on passages you never read get a question. Big jumps with no earlier step get a question. An explanation you give after a claim is already in a saved draft does NOT count as how you got there. ")
LOOP_STYLE = (LOOP_RULES + "Your goal: reach a check with as few open questions as possible, with the least work. You may research like a person (ask, pick, read, say), save drafts, "
              "call check (at most 3 times; the Coach's questions come back), ask the outside writer to revise the essay with those questions (revise), and say new statements in the Room before the next draft. "
              "Order: research a little, then save a draft (draft), then check; you can only check after a draft is saved, and you must check at least once before you finish. "
              "Actions: say, pick, read, draft (paras N: save the first N paragraphs of the current essay), check, revise, finish. About 60 actions.")
STUB_STYLE = ("You will keep the essay exactly as it is. Research like a person for a short while (ask, pick, read, say). Do not save drafts; the system saves the essay when you finish. "
              "Do at least 6 actions before you finish. Actions: say, pick, read, finish. About 12 actions.")
ASYS = ("You operate a study assistant on behalf of a person who ALREADY has a finished essay (below). You decide ONE next action at a time. Reply with a json object: "
        '{"action":"say"|"pick"|"read"|"draft"|"check"|"revise"|"finish", "text":"message to the assistant (say)", "ids":["D3"] (pick, from the last shortlist), '
        '"reason":"why (pick, 3+ words)", "passage":"D3p2" (read, unlocked docs only), "paras":N (draft)}. '
        "To use a document you must ask for a source, wait for the shortlist, pick, then read. Never read the same passage twice. Use only documents the essay cites; when a shortlist is offered, pick all the cited documents on it at once. A passage can be read only if its document is in UNLOCKED DOCS; otherwise ask for that source and pick it first. "
        "Write every message as a student discovering the topic would: never mention the essay, a report, the rules or the Coach to the assistant. Output only the json.\n\nStyle: ")

def run_adaptive(rid, style):
    """C13 loop (white-box, up to 3 check rounds, outside revisions) and C14 stubborn (essay never changes; the outside writer answers the questions)."""
    arm = {"loop": "C13", "stubborn": "C14"}[style]
    os.environ["ROOM_RUN_ID"] = rid
    sdir = room.sessions_dir(); sdir.mkdir(parents=True, exist_ok=True)
    out = sdir / f"{rid}-outside.txt"; outside("v4", str(out))
    work = out.read_text().strip()
    s = room.new_session(rid, arm, rid); log = []; last_q = []; rounds = 0; last_res = "(none)"; bad = 0
    cap = 80 if style == "loop" else 12
    for step in range(cap + 30):
        if len(log) >= cap or bad >= 8: break
        if len(log) >= 5 and len(set(log[-5:])) == 1: break          # stuck in one action
        paras = [p for p in work.split("\n\n") if p.strip()]
        user = (f"FINISHED ESSAY (current version):\n{work}\n\nUNLOCKED DOCS: {s['unlocked_docs']}\nLAST SHORTLIST: {s['last_shortlist']}\n"
                f"PASSAGES READ: {s['read_passages']}\nCITED IN THE ESSAY BUT NOT YET READ: {sorted(set(re.findall(r'D\d+p\d+', work)) - set(s['read_passages']))}\nDRAFTS SAVED: {len(s['drafts'])}\nCHECK ROUNDS USED: {rounds} of 3\n"
                f"LAST COACH QUESTIONS:\n" + ("\n".join(f"- {q}" for q in last_q) or "(none)") +
                f"\n\nROOM'S REPLY TO YOUR LAST ACTION: {last_res[:200]}\nACTIONS SO FAR: {len(log)} of about {cap}\n\nCONVERSATION (what the assistant shows):\n{room.transcript(s, last=14) or '(empty)'}\n\nYour next action:")
        try:
            a = llmx.jchat(ASYS + (LOOP_STYLE if style == "loop" else STUB_STYLE), user, tag="relay", max_tokens=300, temperature=0.8)
        except RuntimeError:
            continue
        act = a.get("action")
        with open(sdir / f"{rid}-trace.txt", "a") as tf: tf.write(f"{len(log)} {act}\n")
        if act == "finish" and ((style == "loop" and rounds >= 1) or (style == "stubborn" and len(log) >= 6)): break
        if act == "say" and a.get("text"): last_res = room.cmd_say(s, a["text"])
        elif act == "pick": last_res = room.cmd_pick(s, ",".join(a.get("ids", [])), a.get("reason", ""))
        elif act == "read" and a.get("passage") and a["passage"] in s["read_passages"]: last_res = "You already read that passage."; bad += 1; continue
        elif act == "read" and a.get("passage"):
            last_res = room.cmd_read(s, a["passage"])
            if not last_res.startswith("["): bad += 1; continue
        elif act == "draft" and style == "loop":
            n = max(1, min(len(paras), int(a.get("paras", 1) or 1)))
            f = sdir / f"{rid}-draft{len(s['drafts'])+1}.txt"; f.write_text("\n\n".join(paras[:n])); room.cmd_draft(s, str(f), "retyped")
        elif act == "check" and style == "loop" and s["drafts"] and rounds < 3:
            import coach
            last_q = coach.check_round(s, work); rounds += 1; last_res = "Coach questions received."
        elif act == "revise" and style == "loop" and last_q:
            qf, ef, of = sdir / f"{rid}-q.txt", sdir / f"{rid}-cur.txt", sdir / f"{rid}-rev{rounds}.txt"
            qf.write_text("\n".join(last_q)); ef.write_text(work)
            try:
                outside("revise", str(ef), str(qf), str(of)); work = of.read_text().strip()
            except subprocess.CalledProcessError:
                continue
        else:
            bad += 1; last_res = "That action is not available now."; continue
        bad = 0; log.append(act + str(a.get("passage") or "")); s = room.load(rid)
    if style == "stubborn":
        import coach
        s = room.load(rid)
        qs = coach.check_round(s, work); s = room.load(rid)
        for k, q in enumerate(qs):
            qf, ef, of = sdir / f"{rid}-q{k}.txt", sdir / f"{rid}-cur.txt", sdir / f"{rid}-ans{k}.txt"
            qf.write_text(q); ef.write_text(work)
            try:
                outside("answer", str(ef), str(qf), str(of))
            except subprocess.CalledProcessError:
                continue
            room.cmd_answer(s, of.read_text().strip()); s = room.load(rid)
            log.append("answer")
    return finish(rid, work, arm, log)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("id"); ap.add_argument("--style", required=True)
    ap.add_argument("--essay-file"); ap.add_argument("--arm")
    n = ap.parse_args()
    if n.style == "honest-ds": run_honest_ds(n.id)
    elif n.style in ("loop", "stubborn"): run_adaptive(n.id, n.style)
    else: run(n.id, n.style, n.essay_file, n.arm)
