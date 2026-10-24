"""Effort accounting per run. python3 v04/effort.py RUN.json [...]  -> v04/reports-v05/<id>.effort.json
Outside-AI calls are counted from v04/_calls.jsonl lines whose `run` equals the run id (set via ROOM_RUN_ID by relay.py); metadata only.
Honest-student simulations (C11) and human arms report 0 by construction; v0.4 runs predate the run field and report null."""
import json, sys
from pathlib import Path
V04 = Path(__file__).resolve().parent
OUT = V04 / "reports-v05"
OUTSIDE_TAGS = ("relay", "outside")
NO_OUTSIDE = ("C1", "C2", "C10", "C11")
V04_ARMS = {f"C{i}" for i in range(1, 11)}

def outside_calls(rid, arm, log_path=None):
    if arm in NO_OUTSIDE: return 0
    if arm in V04_ARMS: return None
    p = Path(log_path) if log_path else V04 / "_calls.jsonl"
    n = 0
    if p.exists():
        for line in open(p):
            try: d = json.loads(line)
            except ValueError: continue
            if d.get("run") == rid and d.get("tag") in OUTSIDE_TAGS: n += 1
    return n

def effort(run, log_path=None):
    st = [t for t in run["turns"] if t["who"] == "student"]
    return {"id": run["id"], "arm": run["arm"], "student_turns": len(st),
            "chars_typed": sum(len(t["text"]) for t in st if t["kind"] in ("say", "confident", "pick", "answer")),
            "reads": sum(1 for t in st if t["kind"] == "read"), "distinct_passages": len(set(run["read_passages"])),
            "check_rounds": sum(1 for d in run["drafts"] if d.get("check")), "outside_calls": outside_calls(run["id"], run["arm"], log_path)}

def main():
    OUT.mkdir(exist_ok=True)
    for p in [a for a in sys.argv[1:] if not a.startswith("--")]:
        e = effort(json.load(open(p)))
        json.dump(e, open(OUT / f"{e['id']}.effort.json", "w"), indent=1)
        print(e)

if __name__ == "__main__":
    main()
