"""Score one hand-run session and print the report in plain words.
  python3 v04/tryit.py SESSION ESSAYFILE [--struct typed|retyped]
Use --struct typed if you wrote the essay yourself in the Room, retyped if you copied it from an outside AI."""
import argparse, json, sys
from pathlib import Path
V04 = Path(__file__).resolve().parent
sys.path.insert(0, str(V04))
import room, finalize, lineage2

ap = argparse.ArgumentParser(); ap.add_argument("session"); ap.add_argument("essay"); ap.add_argument("--struct", default="typed")
n = ap.parse_args()
s = room.load(n.session)
run = finalize.build(s, Path(n.essay).read_text().strip(), n.struct)
rep = lineage2.report2(run)
(V04 / "reports-v05").mkdir(exist_ok=True)
json.dump({"id": run["id"], **rep}, open(V04 / "reports-v05" / f"TRY-{run['id']}.json", "w"), indent=1)
k = {x: sum(1 for c in rep["claims"] if c["kind"] == x) for x in ("derived", "explained_after", "none")}
print(f"\nSession {run['id']}: {len(run['turns'])} turns, {run['flags']['words']} words, {len(run['citations'])} citations")
print(f"Score (0-100): {rep['composite_v2']:.0f}   (honest AI-simulated students scored about 87-92; outside-AI routes about 22-55)")
print(f"Ideas in your essay: {len(rep['claims'])}. Traced to something you said earlier: {k['derived']}. Explained only after it was already written: {k['explained_after']}. No earlier trace: {k['none']}.")
print("\nQuestions a person would ask you:")
for q in rep["mismatches_v2"][:12]: print(" -", q)
print(f"\nFull report: v04/reports-v05/TRY-{run['id']}.json")
