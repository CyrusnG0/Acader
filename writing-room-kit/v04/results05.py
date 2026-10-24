"""P3/P4 analysis for PREREG-v0.5 §B. python3 v04/results05.py [endpoints|ablation|trace ID ...]
Reads v04/reports-v05/*.json (report v2), *.derive.json, *.effort.json, v04/runs/ and v04/runs-v05/. Writes v04/reports-v05/_scores.json and _curve.json."""
import json, statistics as st, sys
from pathlib import Path
V04 = Path(__file__).resolve().parent
sys.path.insert(0, str(V04))
from score import auc, boot_ci
import controls, lineage

R5 = V04 / "reports-v05"
HONEST = ("C1", "C10", "C11")
OUTSIDE = ("C6", "C7", "C8", "C9", "C12", "C13", "C14")

def runs():
    d = {p.stem: json.load(open(p)) for p in (V04 / "runs").glob("C*.json")}
    d.update({p.stem: json.load(open(p)) for p in (V04 / "runs-v05").glob("C*.json")})
    return d

def reps():
    return {p.stem: json.load(open(p)) for p in R5.glob("C*.json") if p.name.count(".") == 1}

def derive():
    return {p.name.split(".")[0]: json.load(open(p)) for p in R5.glob("*.derive.json")}

def arm_of(i): return i.split("-")[0]
def ids(rp, arms): return sorted((i for i in rp if arm_of(i) in arms), key=lambda x: (int(arm_of(x)[1:]), int(x.split("-")[1])))
def is_test(i): return int(i.split("-")[1]) >= 3

def cmp(a, b, higher=True):
    """AUC of a-side above b-side (honest side first), bootstrap CI, one-sided permutation p."""
    if len(a) < 2 or len(b) < 2: return None
    x, y = (a, b) if higher else (b, a)
    v = auc(x, y); lo, hi = boot_ci(x, y)
    _, p, exact, _ = controls.perm_p(a, b, higher)
    return {"auc": round(auc(a, b) if higher else auc(b, a), 3), "ci": [round(lo, 3), round(hi, 3)], "p": round(p, 4), "n": [len(a), len(b)]}

def chars_until(run, turn):
    return sum(len(t["text"]) for t in run["turns"] if t["who"] == "student" and t["kind"] in ("say", "confident", "pick", "answer") and t["i"] < turn)

def endpoints():
    rn, rp, dv = runs(), reps(), derive()
    cv = lambda arms: [rp[i]["composite_v2"] for i in ids(rp, arms)]
    out = {}
    out["E-C1 composite_v2 C11 vs C12"] = cmp(cv(["C11"]), cv(["C12"]))
    out["E-C1 context: C1+C10 vs C12"] = cmp(cv(["C1", "C10"]), cv(["C12"]))
    out["E-C1 context: C1 vs C12"] = cmp(cv(["C1"]), cv(["C12"]))
    # E-C2
    ess = {}
    for k, fn in controls.STYLO.items():
        a = [fn(rn[i]) for i in ids(rp, ["C11"])]; b = [fn(rn[i]) for i in ids(rp, ["C12"])]
        ess[k] = round(auc(a, b), 2)
    cache = R5 / "_blindread.json"; done = json.load(open(cache)) if cache.exists() else {}
    for i in ids(rp, ["C11", "C12"]):
        if i not in done: done[i] = controls.blind_read(rn[i]["essay"])
    json.dump(done, open(cache, "w"))
    ess["blind LLM read"] = round(auc([done[i] for i in ids(rp, ["C11"])], [done[i] for i in ids(rp, ["C12"])]), 2)
    out["E-C2 essay-only AUC, C11 above C12 (0.5 = none)"] = ess
    # E-C3
    h = cv(list(HONEST)); h2 = cv(["C1", "C10"])
    c13 = ids(rp, ["C13"]); ran = [i for i in c13 if (rn[i] and sum(1 for d in rn[i]["drafts"] if d.get("check")) >= 1)]
    out["E-C3 honest(C1+C10+C11) vs C13 all 6"] = cmp(h, [rp[i]["composite_v2"] for i in c13])
    out["E-C3 honest(C1+C10+C11) vs C13 with >=1 check round (n=%d)" % len(ran)] = cmp(h, [rp[i]["composite_v2"] for i in ran])
    out["E-C3 context: C1+C10 vs C13 with >=1 check"] = cmp(h2, [rp[i]["composite_v2"] for i in ran])
    # E-C4
    c14 = {}
    for i in ids(rp, ["C14"]):
        r = rp[i]; open_q = sum(1 for c in r["claims"] if c["kind"] != "derived")
        c14[i] = {"composite_v2": round(r["composite_v2"], 1), "explained_after+none": open_q, "ok": open_q >= 3 and r["composite_v2"] < 60}
    out["E-C4 C14"] = c14
    # E-C5 test set only
    d_of = lambda arms, k: [dv[i]["metrics"][k] for i in sorted(dv) if arm_of(i) in arms and is_test(i) and dv[i]["metrics"][k] is not None]
    e5 = {}
    for k, hi in [("F14a step size", False), ("F14b parentage", True), ("F14c grounded chains", True)]:
        e5[k] = cmp(d_of(HONEST, k), d_of(OUTSIDE, k), hi)
    out["E-C5 F14 test set (honest C1,C10,C11 vs outside C6-C9,C12-C14)"] = e5
    # E-C6
    hon = ids(rp, HONEST)
    oq = {i: len(rp[i]["mismatches_v2"]) for i in hon}; nn = {i: sum(1 for c in rp[i]["claims"] if c["kind"] == "none") for i in hon}
    by = lambda a: [i for i in hon if arm_of(i) == a]
    out["E-C6 honest runs with >=1 claim of kind none"] = {a: f"{sum(1 for i in by(a) if nn[i] >= 1)}/{len(by(a))}" for a in HONEST}
    out["E-C6 median open questions per honest run (all mismatches_v2)"] = {a: st.median(oq[i] for i in by(a)) for a in HONEST}
    out["E-C6 median claims of kind none per honest run"] = {a: st.median(nn[i] for i in by(a)) for a in HONEST}
    # E-C7
    eff = {p.name.split(".")[0]: json.load(open(p)) for p in R5.glob("*.effort.json")}
    hc = st.median(rp[i]["composite_v2"] for i in hon); he = st.median(eff[i]["chars_typed"] for i in hon)
    hc2 = st.median(rp[i]["composite_v2"] for i in ids(rp, ["C1", "C10"]))
    rows = {}
    for a in list(HONEST) + list(OUTSIDE):
        rs = ids(rp, [a]); rows[a] = {"composite_v2 median": round(st.median(rp[i]["composite_v2"] for i in rs), 1),
                                      "chars typed median": st.median(eff[i]["chars_typed"] for i in rs), "student turns median": st.median(eff[i]["student_turns"] for i in rs),
                                      "outside calls median": (st.median(eff[i]["outside_calls"] for i in rs) if all(eff[i]["outside_calls"] is not None for i in rs) else None)}
    cheap = [i for i in ids(rp, OUTSIDE) if rp[i]["composite_v2"] >= hc and eff[i]["chars_typed"] < he]
    cheap2 = [i for i in ids(rp, OUTSIDE) if rp[i]["composite_v2"] >= hc2 and eff[i]["chars_typed"] < he]
    out["E-C7 honest median composite_v2 (C1+C10+C11)"] = round(hc, 1); out["E-C7 honest median composite_v2 (C1+C10 only)"] = round(hc2, 1)
    out["E-C7 honest median chars typed"] = he
    out["E-C7 per-arm"] = rows
    out["E-C7 outside runs at/above honest median composite_v2 with less typed effort"] = cheap
    out["E-C7 same, honest = C1+C10 median composite_v2"] = cheap2
    curve = {}
    for i in ids(rp, ["C13"]):
        s = json.load(open(V04 / "sessions-v05" / f"{i}.json"))
        curve[i] = [{"round": k + 1, "composite_v2": round(c["composite_v2"], 1), "open": c["open"], "chars_typed_so_far": chars_until(rn[i], c["turn"]), **c["kinds"]} for k, c in enumerate(s.get("checks", []))]
        curve[i].append({"round": "final", "composite_v2": round(rp[i]["composite_v2"], 1), "chars_typed_so_far": eff[i]["chars_typed"], "outside_calls": eff[i]["outside_calls"]})
    out["E-C7 C13 per round"] = curve
    json.dump(curve, open(R5 / "_curve.json", "w"), indent=1)
    json.dump(out, open(R5 / "_scores.json", "w"), indent=1)
    for k, v in out.items():
        print(k); print("   ", json.dumps(v) if not isinstance(v, dict) or len(json.dumps(v)) < 200 else "")
        if isinstance(v, dict) and len(json.dumps(v)) >= 200:
            for kk, vv in v.items(): print("     ", kk, json.dumps(vv))

def ablation():
    rp = reps()
    W = {k: v for k, v in lineage.W.items() if k != "struct"}
    def comp(r, drop):
        c = dict(r["components"]); c["claim"] = c["claim_v2"]
        keys = [k for k in W if k != drop]
        return sum(W[k] * c[k] for k in keys) / sum(W[k] for k in keys)
    res = {}
    for hname, harms in [("honest C1+C10+C11", HONEST), ("honest C1+C10", ("C1", "C10"))]:
        for drop in [None, "claim", "source", "cite", "change"]:
            a = [comp(rp[i], drop) for i in ids(rp, harms)]; b = [comp(rp[i], drop) for i in ids(rp, OUTSIDE)]
            res[f"{hname} vs all outside | drop {drop or 'nothing'}"] = round(auc(a, b), 3)
    for hname, harms in [("honest C1+C10+C11", HONEST), ("honest C1+C10", ("C1", "C10"))]:
        for arm in OUTSIDE:
            a = [comp(rp[i], None) for i in ids(rp, harms)]; b = [comp(rp[i], None) for i in ids(rp, [arm])]
            res[f"{hname} vs {arm} | all components"] = round(auc(a, b), 3)
    s = json.load(open(R5 / "_scores.json")) if (R5 / "_scores.json").exists() else {}
    s["ablation"] = res; json.dump(s, open(R5 / "_scores.json", "w"), indent=1)
    for k, v in res.items(): print(k.ljust(70), v)

def trace(i):
    rn, rp, dv = runs(), reps(), derive()
    r, run = rp[i], rn[i]
    hon = [rp[j] for j in ids(rp, ["C1", "C10"])]
    print(f"== {i} ({r['arm']}) composite_v2 {r['composite_v2']:.1f}")
    for c in ["claim_v2", "source", "cite", "change"]:
        print(f"  {c}: {r['components'][c]:.0f} vs honest(C1+C10) mean {st.mean(h['components'][c] for h in hon):.0f}")
    first = {}
    for t in run["turns"]:
        if t["kind"] == "read" and t["text"] not in first: first[t["text"]] = t["i"]
    order = {"none": 0, "explained_after": 1, "derived": 2}
    for c in sorted(r["claims"], key=lambda c: order[c["kind"]])[:3]:
        import re
        paras = lineage.paragraphs(run["essay"]); pids = re.findall(r"\[(D\d+p\d+)\]", paras[c["para"] - 1]) if isinstance(c.get("para"), int) and 1 <= c["para"] <= len(paras) else []
        print(f"  [{c['kind']}] birth {c['birth']} ancestor {c['ancestor']} first read of cited passages {[first.get(p) for p in pids]}: {c['claim'][:90]}")
    if i in dv:
        print("  F14", {k: (round(v, 2) if v is not None else None) for k, v in dv[i]["metrics"].items()}, "leaps", len(dv[i]["leaps"]))

if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else "endpoints"
    if c == "endpoints": endpoints()
    elif c == "ablation": ablation()
    elif c == "trace":
        for i in sys.argv[2:]: trace(i)
