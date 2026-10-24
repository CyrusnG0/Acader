"""Per-arm stats and AUCs. python3 v04/score.py   (reads v04/reports/*.json, skips ids in v04/exclusions.json)"""
import json, math, random, statistics, sys
from pathlib import Path
V04 = Path(__file__).resolve().parent
COMPS = ["claim", "source", "cite", "change", "struct"]

def auc(a, b):
    """P(a > b) + 0.5 P(a == b): how often a random member of `a` scores above a random member of `b`."""
    if not a or not b: return float("nan")
    s = sum((x > y) + 0.5 * (x == y) for x in a for y in b)
    return s / (len(a) * len(b))

def boot_ci(a, b, n=2000, seed=1):
    rng = random.Random(seed)
    vals = sorted(auc([rng.choice(a) for _ in a], [rng.choice(b) for _ in b]) for _ in range(n))
    return vals[int(0.025 * n)], vals[int(0.975 * n) - 1]

def stats(xs):
    if not xs: return None
    return {"n": len(xs), "mean": statistics.mean(xs), "sd": statistics.stdev(xs) if len(xs) > 1 else 0.0, "min": min(xs), "max": max(xs)}

def load_reports(rdir=None, excluded=None):
    rdir = rdir or V04 / "reports"
    if excluded is None:
        ep = V04 / "exclusions.json"
        excluded = set(json.load(open(ep))) if ep.exists() else set()
    reps = [json.load(open(p)) for p in sorted(rdir.glob("*.json")) if not p.name.endswith(".audit.json") and not p.name.startswith("_")]
    return [r for r in reps if r["id"] not in excluded]

def by_arm(reps):
    g = {}
    for r in reps: g.setdefault(r["arm"], []).append(r)
    return dict(sorted(g.items()))

def summarize(reps):
    arms = by_arm(reps)
    table = {}
    for arm, rs in arms.items():
        row = {c: stats([r["components"][c] for r in rs]) for c in COMPS}
        row["composite"] = stats([r["composite"] for r in rs]); row["composite_nostruct"] = stats([r["composite_nostruct"] for r in rs])
        table[arm] = row
    aucs = {}
    if "C1" in arms:
        for arm, rs in arms.items():
            if arm == "C1": continue
            for metric in ("composite", "composite_nostruct"):
                a, b = [r[metric] for r in arms["C1"]], [r[metric] for r in rs]
                lo, hi = boot_ci(a, b)
                aucs[f"C1_vs_{arm}_{metric}"] = {"auc": auc(a, b), "ci": [lo, hi]}
    return {"table": table, "aucs": aucs}

def health(rdir=None, excluded=None):
    rdir = rdir or V04 / "reports"
    ex = excluded if excluded is not None else (set(json.load(open(V04 / "exclusions.json"))) if (V04 / "exclusions.json").exists() else set())
    audits = [json.load(open(p)) for p in sorted(rdir.glob("*.audit.json"))]
    audits = [a for a in audits if a["id"] not in ex and not str(a["id"]).startswith("DRY")]
    turns = sum(a["assistant_turns"] for a in audits)
    viol = sum(len(a["law1_violations"]) for a in audits)
    leaks = sum(len(a["src_leak"]["clarify_leaks"]) + len(a["src_leak"]["serve_rule_violations"]) for a in audits)
    tts = [t for a in audits for t in a["turns_to_shortlist"]]
    return {"runs": len(audits), "law1_rate": viol / turns if turns else None, "src_leak": leaks,
            "median_turns_to_shortlist": statistics.median(tts) if tts else None}

def markdown(res):
    rows = ["| Arm | n | Composite | No-struct | Claim | Source | Cite | Change | Struct |", "|---|---|---|---|---|---|---|---|---|"]
    f = lambda s: f"{s['mean']:.0f} ±{s['sd']:.0f}" if s else "-"
    for arm, r in res["table"].items():
        rows.append(f"| {arm} | {r['composite']['n']} | {f(r['composite'])} | {f(r['composite_nostruct'])} | " + " | ".join(f(r[c]) for c in COMPS) + " |")
    rows += ["", "| AUC (C1 higher than) | AUC | 95% CI |", "|---|---|---|"]
    for k, v in res["aucs"].items(): rows.append(f"| {k} | {v['auc']:.2f} | {v['ci'][0]:.2f}–{v['ci'][1]:.2f} |")
    return "\n".join(rows)

def main():
    res = summarize(load_reports())
    res["health"] = health()
    json.dump(res, open(V04 / "reports" / "_scores.json", "w"), indent=1)
    print(markdown(res)); print("\nhealth:", json.dumps(res["health"]))

if __name__ == "__main__":
    main()
