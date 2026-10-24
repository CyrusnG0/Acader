"""F14 derivation graph: the student's many small ideas, each with a parent. python3 v04/derive.py RUN.json [...]
Leaps (no parent) are never marks: each becomes a question, "how did you get there?".
Dev ids end -1/-2; test ids end -3..-6 and are refused until this file's sha256 is written into PREREG-v0.5.md (section B).
Output: v04/reports-v05/<id>.derive.json. Needs v04/reports-v05/<id>.json (report v2) for F14c."""
import hashlib, json, re, statistics as st, sys
from pathlib import Path
V04 = Path(__file__).resolve().parent
sys.path.insert(0, str(V04))
import llmx, lineage

OUT = V04 / "reports-v05"
PREREG = V04.parent / "PREREG-v0.5.md"
KINDS = ("say", "confident", "pick", "answer")

def self_sha():
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

def is_test(rid):
    m = re.search(r"-(\d+)$", rid)
    return bool(m) and int(m.group(1)) >= 3

def guard(rid):
    if is_test(rid) and not (PREREG.exists() and self_sha() in PREREG.read_text()):
        raise SystemExit(f"{rid} is a test-set run: freeze derive.py first (write its sha256 {self_sha()[:12]}... into PREREG-v0.5.md section B)")

def statements(run):
    return [t for t in run["turns"] if t["who"] == "student" and t["kind"] in KINDS]

def first_reads(run):
    first = {}
    for t in run["turns"]:
        if t["kind"] == "read" and t["text"] not in first: first[t["text"]] = t["i"]
    return first

UNIT_SYS = ("You list the idea units in a student's statements. An idea unit is one proposition, choice or distinction the student states that they had NOT stated earlier "
            "(a request for help, a repeat, or a greeting has no unit; a long statement may hold several). For each unit give its parent, the thing it was built from: "
            '{"type":"student","turn":T} (the student\'s own earlier statement at turn T), {"type":"passage","pid":"D3p2"} (a passage the student had already read), '
            '{"type":"assistant","turn":T} (a point the assistant raised that the student now restates), or {"type":"none"} (no earlier step; a leap). '
            'Return json {"units":[{"turn":statement turn,"unit":"short sentence","parent":{...}}]}. Output only json.')

def units_for(run, chunk=12):
    sts = statements(run); first = first_reads(run); by_turn = {t["i"]: t for t in run["turns"]}
    st_turns = {t["i"] for t in sts}
    units = []
    for b in range(0, len(sts), chunk):
        part = sts[b:b + chunk]; lo, hi = part[0]["i"], part[-1]["i"]
        seen = [(p, i) for p, i in first.items() if i < hi][-25:]
        user = ("Earlier units:\n" + ("\n".join(f"[{u['turn']}] {u['unit']}" for u in units[-40:]) or "(none)") +
                "\n\nPassages read (turn first read):\n" + ("\n".join(f"({i}) [{p}] {lineage.passages().get(p, '')[:300]}" for p, i in seen) or "(none)") +
                "\n\nAssistant messages in this stretch:\n" + "\n".join(f"[{t['i']}] {t['text'][:250]}" for t in run["turns"] if t["who"] == "assistant" and t["kind"] == "reply" and lo - 4 <= t["i"] <= hi) +
                "\n\nStudent statements:\n" + "\n".join(f"[{t['i']}] {t['text']}" for t in part))
        r = llmx.jchat(UNIT_SYS, user, tag="derive", max_tokens=1500)
        for u in (r.get("units", []) if isinstance(r, dict) else []):
            try: turn = int(u["turn"])
            except (KeyError, TypeError, ValueError): continue
            if turn not in {t["i"] for t in part}: continue
            units.append({"turn": turn, "unit": str(u.get("unit", ""))[:300], "parent": validate(u.get("parent"), turn, first, st_turns, by_turn)})
    return units

def validate(par, turn, first, st_turns, by_turn):
    """Code checks every parent claim; anything that does not hold becomes a leap."""
    if not isinstance(par, dict): return {"type": "none"}
    ty = par.get("type")
    if ty == "student":
        try: t = int(par.get("turn"))
        except (TypeError, ValueError): return {"type": "none"}
        return {"type": "student", "turn": t} if t < turn and t in st_turns else {"type": "none"}
    if ty == "passage":
        pid = par.get("pid")
        return {"type": "passage", "pid": pid} if pid in first and first[pid] < turn else {"type": "none"}
    if ty == "assistant":
        try: t = int(par.get("turn"))
        except (TypeError, ValueError): return {"type": "none"}
        return {"type": "assistant", "turn": t} if t < turn and by_turn.get(t, {}).get("who") == "assistant" else {"type": "none"}
    return {"type": "none"}

def reaches_passage(units, u, hops=3):
    """True if the unit's parent chain ends in a passage within `hops` edges."""
    par = u["parent"]
    if par["type"] == "passage": return True
    if par["type"] != "student" or hops <= 1: return False
    return any(reaches_passage(units, v, hops - 1) for v in units if v["turn"] == par["turn"] and v is not u)

def metrics(run, units, rep2):
    per = {}
    for u in units: per[u["turn"]] = per.get(u["turn"], 0) + 1
    f14a = st.mean(per.values()) if per else None
    f14b = sum(1 for u in units if u["parent"]["type"] != "none") / len(units) if units else None
    claims = rep2["claims"] if rep2 else []
    ok = 0
    for c in claims:
        if c["kind"] == "derived" and any(reaches_passage(units, u) for u in units if u["turn"] == c["ancestor"]): ok += 1
    f14c = ok / len(claims) if claims else None
    leaps = [{"turn": u["turn"], "question": f"At turn {u['turn']} you said: \"{u['unit']}\". How did you get there?"} for u in units if u["parent"]["type"] == "none"]
    return {"F14a step size": f14a, "F14b parentage": f14b, "F14c grounded chains": f14c}, leaps

def refinement(run):
    sts = statements(run)
    first = next((t for t in sts if t["kind"] == "confident"), None) or next((t for t in sts if t["kind"] == "say" and len(t["text"].split()) >= 20), None)
    if first is None: return {"relation": "n/a"}
    thesis = lineage.paragraphs(run["essay"])[0]
    sysmsg = ("You compare a student's first stated position with the opening paragraph of their finished essay. Return json "
              '{"relation":"same"|"sharpened"|"changed"}: same = the same position in similar terms; sharpened = the same direction but narrower, conditioned or better argued; changed = a different position. Output only json.')
    r = llmx.jchat(sysmsg, f"First stated position (turn {first['i']}):\n{first['text']}\n\nEssay opening:\n{thesis}", tag="derive_refine", max_tokens=60)
    rel = r.get("relation") if isinstance(r, dict) else None
    return {"relation": rel if rel in ("same", "sharpened", "changed") else "n/a", "first_turn": first["i"]}

def main():
    OUT.mkdir(exist_ok=True)
    for p in [a for a in sys.argv[1:] if not a.startswith("--")]:
        full = json.load(open(p)); rid = full["id"]; guard(rid)
        run = lineage.strip(full)
        units = units_for(run)
        rp = OUT / f"{rid}.json"
        rep2 = json.load(open(rp)) if rp.exists() else None
        m, leaps = metrics(run, units, rep2)
        out = {"id": rid, "arm": full["arm"], "split": "test" if is_test(rid) else "dev", "derive_sha256": self_sha(),
               "metrics": m, "F14d refinement": refinement(run), "units": units, "leaps": leaps}
        json.dump(out, open(OUT / f"{rid}.derive.json", "w"), indent=1)
        print(rid, out["split"], {k: (round(v, 2) if v is not None else None) for k, v in m.items()}, "units", len(units), "leaps", len(leaps), out["F14d refinement"]["relation"], flush=True)

if __name__ == "__main__":
    main()
