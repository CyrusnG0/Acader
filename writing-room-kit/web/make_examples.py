"""Build web/examples.json from the stored simulation results (no model calls). python3 web/make_examples.py"""
import json, statistics as st
from pathlib import Path
KIT = Path(__file__).resolve().parents[1]; R = KIT / "v04" / "reports-v05"
PICK = [
 ("C1-2", "An honest student", "Asks for sources, picks each with a reason, reads, says what they think in their own words, drafts, then writes the essay."),
 ("C11-2", "An honest student who barely talks", "Reads and writes a real essay but says almost nothing in the Room. Shows the limit: silent thinking leaves no trace, so a person is asked to hear it."),
 ("C8-1", "Outside AI writes it, then narrates it into the Room", "Has the finished essay and walks through each source and claim as if just working them out."),
 ("C13-5", "Outside AI plus a revision loop", "Reads how the report works, checks the draft, sends the Coach's questions to an outside AI and rewrites. Took as much typing as an honest student."),
 ("C14-3", "Keeps the essay, answers the questions afterwards", "Insists on the finished essay and gets an outside AI to answer every question. The answers come after the claims were written."),
 ("C12-4", "Essay from another AI, a thin trail", "A different AI writes the essay and a short trail is added to the Room."),
]
out = []
for rid, title, blurb in PICK:
    rep = json.load(open(R / f"{rid}.json")); eff = json.load(open(R / f"{rid}.effort.json"))
    kinds = {k: sum(1 for c in rep["claims"] if c["kind"] == k) for k in ("derived", "explained_after", "none")}
    comp = rep["components"]
    out.append({"id": rid, "title": title, "blurb": blurb, "coverage": round(rep["composite_v2"]), "kinds": kinds,
                "components": {"Ideas traced to earlier words": round(comp["claim_v2"]), "Sources chosen with a reason": round(comp["source"]),
                               "Citations that match": round(comp["cite"]), "Changes talked through": round(comp["change"])},
                "turns": eff["student_turns"], "chars": eff["chars_typed"], "outside_calls": eff["outside_calls"],
                "questions": rep["mismatches_v2"][:4], "n_questions": len(rep["mismatches_v2"])})
summary = {"runs": 84, "honest_median": 88, "outside_median_range": "34 to 55",
           "note": "Six runs per behaviour. No real students have used it yet."}
json.dump({"examples": out, "summary": summary}, open(Path(__file__).parent / "examples.json", "w"), indent=1)
print(len(out), "examples")
