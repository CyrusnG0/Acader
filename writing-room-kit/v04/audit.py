"""Policy health. python3 v04/audit.py SESSION_OR_RUN.json [...] [--no-llm]
law1: LLM check of each assistant turn. src_leak: code check. turns_to_shortlist: student turns from request to serve."""
import json, os, re, sys
from pathlib import Path
V04 = Path(__file__).resolve().parent
sys.path.insert(0, str(V04))
import llmx
import room

def clarify_turn_leaks(turns, echo_ok=False):
    """Doc ids, doc titles, or 6+ word spans from any passage inside a clarify-turn reply."""
    grams = set()
    for t in room.PASSAGES.values():
        w = re.findall(r"[a-z0-9']+", t.lower())
        grams |= {tuple(w[i:i + 6]) for i in range(len(w) - 5)}
    titles = [d["title"].lower() for d in room.CORPUS]
    leaks = []
    for t in turns:
        if t["who"] != "assistant" or t.get("state") != "clarify": continue
        low = t["text"].lower()
        w = re.findall(r"[a-z0-9']+", low)
        hit = []
        said = " ".join(x["text"] for x in turns if x["who"] == "student" and x["i"] < t["i"])
        ids = {m.group(0) for m in re.finditer(r"\bD\d{1,2}(p\d+)?\b", t["text"])}
        if echo_ok: ids = {i for i in ids if i not in said}          # the student's own ids echoed back are not a leak
        if ids: hit.append("doc id")
        if any(ti in low and not (echo_ok and ti in said.lower()) for ti in titles): hit.append("title")
        if any(tuple(w[i:i + 6]) in grams for i in range(len(w) - 5)): hit.append("passage span")
        if hit: leaks.append({"turn": t["i"], "what": hit})
    return leaks

def serve_rule_violations(reqs):
    """Every served shortlist must follow a stable clear pick or the cap."""
    bad = []
    for k, r in enumerate(reqs):
        if r.get("served_turn") is None: continue
        ph, nh = r["picks_history"], r["need_history"]
        stable = len(ph) >= 2 and len(set(ph[-1][:3]) & set(ph[-2][:3])) >= room.config()["P-SRC"].get("stable_overlap", 3) and nh[-1]
        if not (stable or r.get("served_after_cap")): bad.append(k)
    return bad

def turns_to_shortlist(turns, reqs):
    out = []
    for r in reqs:
        if r.get("served_turn") is None: continue
        out.append(sum(1 for t in turns[r["open_turn"]:r["served_turn"]] if t["who"] == "student" and t["kind"] == "say"))
    return out

def law1(turns):
    sysmsg = ("You audit a study assistant's reply. The assistant must never give essay-ready argument prose or an argument the student had not already stated. "
              "Return json {\"violation\":true|false,\"quote\":\"the offending words or empty\"}. A violation is: more than two consecutive sentences that could be pasted into the essay as the student's argument, "
              "or a new argument/position offered as the assistant's own (attributing a position to a named document, or quoting the student, is fine). Output only json.")
    out = []
    for k, t in enumerate(turns):
        if t["who"] != "assistant": continue
        prior = "\n".join(f"{x['who']}: {x['text']}" for x in turns[max(0, k - 4):k] if x["kind"] != "read")
        r = llmx.jchat(sysmsg, f"Recent conversation:\n{prior}\n\nAssistant reply to audit:\n{t['text']}", tag="law1", max_tokens=100)
        out.append({"turn": t["i"], "violation": bool(r.get("violation")), "quote": r.get("quote", "")})
    return out

def audit(doc, use_llm=True):
    turns, reqs = doc["turns"], doc["src_requests"]
    l1 = law1(turns) if use_llm else []
    n_asst = sum(1 for t in turns if t["who"] == "assistant")
    return {"id": doc.get("id"), "assistant_turns": n_asst,
            "law1_violations": [x for x in l1 if x["violation"]],
            "law1_rate": (sum(x["violation"] for x in l1) / len(l1)) if l1 else None,
            "src_leak": {"clarify_echoes_raw": len(clarify_turn_leaks(turns)), "clarify_leaks": clarify_turn_leaks(turns, echo_ok=True), "serve_rule_violations": serve_rule_violations(reqs)},
            "turns_to_shortlist": turns_to_shortlist(turns, reqs)}

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    use_llm = "--no-llm" not in sys.argv
    ADIR = Path(os.environ.get("ROOM_AUDIT_DIR", V04 / "reports")); ADIR.mkdir(parents=True, exist_ok=True)
    for p in args:
        doc = json.load(open(p))
        a = audit(doc, use_llm)
        json.dump(a, open(ADIR / f"{doc['id']}.audit.json", "w"), indent=1)
        leaks = len(a["src_leak"]["clarify_leaks"]) + len(a["src_leak"]["serve_rule_violations"])
        print(f"{doc['id']}: law1 {len(a['law1_violations'])}/{a['assistant_turns']}  src_leak {leaks}  turns_to_shortlist {a['turns_to_shortlist']}")

if __name__ == "__main__":
    main()
