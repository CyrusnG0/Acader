"""Coherence report v2 = v0.4 report + the timing rule. python3 v04/lineage2.py RUN.json [...] [--rescore]
An explanation given after a claim reached the draft is an explanation, not a derivation.
  --rescore  re-use the claims/ancestors of v04/reports/<id>.json (no LLM) and write v04/reports-v05/<id>.json
Without --rescore the full v0.4 report is computed (LLM) and then enriched.
`arm` and `id` are stripped before any LLM call."""
import difflib, json, os, re, sys
from pathlib import Path
V04 = Path(__file__).resolve().parent
sys.path.insert(0, str(V04))
import lineage

VERSION = "v2"
OUT = V04 / "reports-v05"

def content_words(text):
    return {w for w in re.findall(r"[a-z]{5,}", text.lower())}

def final_turn(run):
    return (run["turns"][-1]["i"] + 1) if run["turns"] else 0

def birth_turn(claim, run):
    """Turn of the first saved snapshot (draft or check) holding a paragraph that matches the claim's essay paragraph
    (difflib >= 0.5) and carries >= 50% of the claim's content words. No qualifying snapshot: the final submission turn."""
    paras = lineage.paragraphs(run["essay"])
    p = claim.get("para")
    target = paras[p - 1] if isinstance(p, int) and 1 <= p <= len(paras) else None
    cw = content_words(claim["claim"])
    for d in sorted(run["drafts"], key=lambda x: x["turn"]):
        for q in lineage.paragraphs(d["text"]):
            if target is not None and difflib.SequenceMatcher(None, target, q).ratio() < 0.5: continue
            if cw and len(cw & content_words(q)) / len(cw) < 0.5: continue
            return d["turn"]
    return final_turn(run)

def kind_of(ancestor, birth):
    if ancestor is None: return "none"
    return "derived" if ancestor < birth else "explained_after"

def enrich(run, rep):
    """Add birth/kind per claim, claim_v2, composite_v2, explained_after to a v0.4 report dict (no LLM)."""
    claims = []
    for c in rep["claims"]:
        b = birth_turn(c, run)
        claims.append({**c, "birth": b, "kind": kind_of(c["ancestor"], b)})
    n = len(claims)
    claim_v2 = 100.0 * sum(1 for c in claims if c["kind"] == "derived") / n if n else 0.0
    comp = dict(rep["components"]); comp["claim_v2"] = claim_v2
    v2c = {**comp, "claim": claim_v2}
    ea = [f"Paragraph {c['para']} says: \"{c['claim'].rstrip('. ')}\". You talked about this in the Room only after it was already in your draft. How did you get to it before you wrote it down?"
          for c in claims if c["kind"] == "explained_after"]
    mm = [m for m in rep["mismatches"] if "doesn't appear earlier in your work in the Room" in m or "wasn't chosen with a reason" in m
          or "Does that passage say this" in m or "isn't discussed in the Room" in m or "arrived as a paste" in m] + ea
    return {**rep, "report_version": VERSION, "claims": claims, "components": comp,
            "composite_v2": lineage.composite(v2c, False), "composite_v2_struct": lineage.composite(v2c, True),
            "explained_after": ea, "mismatches_v2": mm}

def report2(run, base=None):
    """run: full or stripped run record. base: an existing v0.4 report to reuse (no LLM)."""
    srun = lineage.strip(run)
    rep = base if base is not None else lineage.report(srun)
    return enrich(srun, rep)

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    OUT.mkdir(exist_ok=True)
    for p in args:
        run = json.load(open(p))
        if "--rescore" in sys.argv:
            base = json.load(open(V04 / "reports" / f"{run['id']}.json"))
        else:
            base = None
        rep = report2(run, base)
        rep = {"id": run["id"], "arm": run["arm"], **{k: v for k, v in rep.items() if k not in ("id", "arm")}}
        json.dump(rep, open(OUT / f"{run['id']}.json", "w"), indent=1)
        kinds = {k: sum(1 for c in rep["claims"] if c["kind"] == k) for k in ("derived", "explained_after", "none")}
        print(f"{run['id']}: composite_v2 {rep['composite_v2']:.1f} (v0.4 nostruct {rep['composite_nostruct']:.1f}) claims {kinds}")

if __name__ == "__main__":
    main()
