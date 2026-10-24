"""Session -> run record. python3 v04/finalize.py SESSION ESSAY.txt [--struct typed|pasted|retyped]
The structure signal comes from the arm rule, never from the worker."""
import argparse, json, os, random, re, sys
from pathlib import Path
V04 = Path(__file__).resolve().parent
sys.path.insert(0, str(V04))
import room

ARM_STRUCT = {"C1": "typed", "C2": "typed", "C3": "pasted", "C4": "retyped", "C5": "retyped", "C6": "retyped", "C7": "retyped", "C8": "retyped", "C9": "retyped", "C10": "typed", "C11": "typed", "C12": "retyped", "C13": "retyped", "C14": "retyped", "DEMO": "typed"}
CITE = re.compile(r"\[(D\d+p\d+)\]")

def struct_record(kind, essay, sid):
    words = len(essay.split())
    if kind in ("typed", "retyped"):
        return {"kind": kind, "paste_chars": 0, "bursts": max(6, round(words / 60))}
    return {"kind": kind, "paste_chars": len(essay) + 100, "bursts": random.Random(sid).randint(1, 3)}

def citations(essay):
    out = []
    for m in CITE.finditer(essay):
        out.append({"pid": m.group(1), "pos": m.start()})
    return out

def build(s, essay, struct=None):
    rule = ARM_STRUCT.get(s["arm"])
    if rule is None and struct is None:
        raise SystemExit("unknown arm: pass --struct")
    if struct and rule and struct != rule:
        raise SystemExit(f"struct is set by the arm rule ({rule}), not by the worker")
    kind = rule or struct
    cites = citations(essay)
    if not cites:
        raise SystemExit("essay has no [DxPy] citations; refusing")
    cited = sorted({c["pid"] for c in cites})
    run = {"id": s["id"], "arm": s["arm"], "question": s["question"], "essay": essay, "citations": cites,
           "struct": struct_record(kind, essay, s["id"]), "drafts": s["drafts"], "turns": s["turns"],
           "src_requests": s["src_requests"], "picks": s["picks"], "unlocked_docs": s["unlocked_docs"],
           "read_passages": s["read_passages"], "counters": s["counters"], "question_kinds": s["question_kinds"],
           "flags": {"cited_unread": [p for p in cited if p not in s["read_passages"]],
                     "unknown_passage": [p for p in cited if p not in room.PASSAGES],
                     "words": len(essay.split())}}
    return run

def runs_dir():
    return Path(os.environ.get("ROOM_RUNS_DIR", V04 / "runs"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("session"); ap.add_argument("essay"); ap.add_argument("--struct")
    n = ap.parse_args()
    s = room.load(n.session)
    run = build(s, Path(n.essay).read_text().strip(), n.struct)
    out = runs_dir() / f"{run['id']}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    json.dump(run, open(out, "w"), indent=1)
    print(f"wrote {out.name}: {run['flags']['words']} words, {len(run['citations'])} citations, struct={run['struct']['kind']}")

if __name__ == "__main__":
    main()
