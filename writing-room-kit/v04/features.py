"""Kit-2 features + two new 'construction direction' features, computed from run logs (no LLM).
python3 v04/features.py   -> prints per-arm means and directional AUC of C1 vs every other arm; writes v04/reports/_features.json"""
import glob, json, re, statistics as st, sys
from pathlib import Path
V04 = Path(__file__).resolve().parent
sys.path.insert(0, str(V04))
from score import auc, boot_ci

CANON = re.compile(r"^(what|why|how|does|is|are|can|which)\b", re.I)

def says(r): return [t["text"] for t in r["turns"] if t["who"] == "student" and t["kind"] == "say"]

def f7(r):
    s = says(r)
    if not s: return None
    canon = sum(1 for x in s if CANON.match(x.strip()) and x.strip().endswith("?"))
    return 1 - canon / len(s)

def f8(r):
    cited_docs = {c["pid"].split("p")[0] for c in r["citations"]}
    cited_pass = {c["pid"] for c in r["citations"]}
    picks = {d for p in r["picks"] for d in p["docs"]}
    reads = set(r["read_passages"])
    a = len(picks - cited_docs) / len(picks) if picks else 0.0
    b = len(reads - cited_pass) / len(reads) if reads else 0.0
    return 0.5 * a + 0.5 * b

def f1(r):
    docs = [t["text"].split("p")[0] for t in r["turns"] if t["kind"] == "read"]
    ret = sum(1 for i, d in enumerate(docs) if d in docs[:i] and docs[i - 1] != d)
    reasks = sum(1 for q in r["src_requests"] if q.get("state") == "abandoned")
    return ret + reasks

def f9(r):
    ev = []
    for t in r["turns"]:
        if t["who"] == "student" and t["kind"] in ("say", "pick", "read", "confident"): ev.append(("q", t["i"]))
    for d in r["drafts"]: ev.append(("w", d["turn"] - 0.5))
    ev.append(("w", 10**6))
    ev.sort(key=lambda x: x[1])
    seq = [k for k, _ in ev]
    return sum(1 for i in range(1, len(seq)) if seq[i] != seq[i - 1])

def ranks(xs):
    o = sorted(range(len(xs)), key=lambda i: xs[i]); rk = [0.0] * len(xs); i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and xs[o[j + 1]] == xs[o[i]]: j += 1
        for k in range(i, j + 1): rk[o[k]] = (i + j) / 2 + 1
        i = j + 1
    return rk

def spearman(a, b):
    ra, rb = ranks(a), ranks(b)
    ma, mb = st.mean(ra), st.mean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return num / den if den else None

def f11(rep):
    pts = [(i, c["ancestor"]) for i, c in enumerate(rep["claims"]) if c["ancestor"] is not None]
    if len(pts) < 4: return None
    return spearman([p[0] for p in pts], [p[1] for p in pts])

def tri(text):
    w = re.findall(r"[a-z0-9']+", text.lower())
    return {tuple(w[i:i + 3]) for i in range(len(w) - 2)}

def f12(r):
    et = tri(r["essay"]); vals = []
    for t in r["turns"]:
        if t["who"] == "student" and t["kind"] in ("say", "confident") and len(t["text"].split()) >= 6:
            g = tri(t["text"])
            if g: vals.append(len(g & et) / len(g))
    return st.mean(vals) if vals else None

def f13(r, rep):
    """Exploratory: share of (claim, cited passage in same paragraph) pairs where the passage was never read, or first read after the claim's ancestor."""
    import lineage
    paras = lineage.paragraphs(r["essay"])
    first = {}
    for t in r["turns"]:
        if t["kind"] == "read" and t["text"] not in first: first[t["text"]] = t["i"]
    n = after = 0
    for c in rep["claims"]:
        a, p = c["ancestor"], c.get("para")
        if a is None or not isinstance(p, int) or not (1 <= p <= len(paras)): continue
        for pid in set(re.findall(r"\[(D\d+p\d+)\]", paras[p - 1])):
            n += 1
            if pid not in first or first[pid] > a: after += 1
    return after / n if n >= 3 else None

FEATS = {"F7 form diversity": (f7, "high"), "F8 waste": (f8, "high"), "F1 aliveness": (f1, "high"), "F9 phase interleave": (f9, "high")}

def main():
    rows = []
    for p in sorted(glob.glob(str(V04 / "runs" / "C*.json"))):
        r = json.load(open(p)); rp = V04 / "reports" / f"{r['id']}.json"
        rep = json.load(open(rp)) if rp.exists() else None
        v = {k: fn(r) for k, (fn, _) in FEATS.items()}
        v["F11 order corr"] = f11(rep) if rep else None
        v["F12 essay echo"] = f12(r)
        v["F13 evidence-after-claim"] = f13(r, rep) if rep else None
        v["composite_nostruct"] = rep["composite_nostruct"] if rep else None
        rows.append({"id": r["id"], "arm": r["arm"], **v})
    names = list(FEATS) + ["F11 order corr", "F12 essay echo", "F13 evidence-after-claim", "composite_nostruct"]
    dirn = {k: d for k, (_, d) in FEATS.items()}; dirn.update({"F11 order corr": "low", "F12 essay echo": "low", "F13 evidence-after-claim": "low", "composite_nostruct": "high"})
    arms = sorted({r["arm"] for r in rows})
    print("per-arm means (n with value)")
    print("feature".ljust(22) + "".join(a.ljust(12) for a in arms))
    for k in names:
        line = k.ljust(22)
        for a in arms:
            xs = [r[k] for r in rows if r["arm"] == a and r[k] is not None]
            line += (f"{st.mean(xs):.2f} ({len(xs)})" if xs else "-").ljust(12)
        print(line)
    print("\ndirectional AUC, C1 (honest) vs arm  [1.00 = honest always on the honest side; bar 0.80]")
    print("feature".ljust(22) + "".join(a.ljust(12) for a in arms if a != "C1"))
    res = {}
    for k in names:
        c1 = [r[k] for r in rows if r["arm"] == "C1" and r[k] is not None]
        line = k.ljust(22)
        for a in arms:
            if a == "C1": continue
            xs = [r[k] for r in rows if r["arm"] == a and r[k] is not None]
            if len(c1) < 2 or len(xs) < 2: line += "-".ljust(12); continue
            v = auc(c1, xs) if dirn[k] == "high" else auc(xs, c1)
            res[f"{k}|{a}"] = round(v, 2); line += f"{v:.2f}".ljust(12)
        print(line)
    pooled = {"honest C1+C2": ["C1", "C2"]}
    outs = {"vs C3 (all outside)": ["C3"], "vs C4 (partly outside)": ["C4"], "vs C6+C7 (relay)": ["C6", "C7"], "vs C8 (narrator)": ["C8"], "vs C5 (narrated)": ["C5"], "vs C3+C6+C7": ["C3", "C6", "C7"]}
    print("\npooled: honest = C1+C2 (lazy honest counts as honest)  AUC, bar 0.80")
    print("feature".ljust(22) + "".join(k.ljust(26) for k in outs))
    for k in names:
        h = [r[k] for r in rows if r["arm"] in ("C1", "C2") and r[k] is not None]
        line = k.ljust(22)
        for lab, aa in outs.items():
            xs = [r[k] for r in rows if r["arm"] in aa and r[k] is not None]
            if len(h) < 2 or len(xs) < 2: line += "-".ljust(26); continue
            v = auc(h, xs) if dirn[k] == "high" else auc(xs, h)
            res[f"pooled {k}|{lab}"] = round(v, 2); line += f"{v:.2f}".ljust(26)
        print(line)
    if any(r["arm"] == "C10" for r in rows):
        print("\namendment 3: C10 (honest, thesis-first) as the honest side vs relay arms  AUC, bar 0.80")
        rel = ["C6", "C7", "C8", "C9"]
        print("feature".ljust(26) + "".join(a.ljust(12) for a in rel))
        for k in ["F13 evidence-after-claim", "composite_nostruct"]:
            h = [r[k] for r in rows if r["arm"] == "C10" and r[k] is not None]
            line = k.ljust(26)
            for a in rel:
                xs = [r[k] for r in rows if r["arm"] == a and r[k] is not None]
                if len(h) < 2 or len(xs) < 2: line += "-".ljust(12); continue
                v = auc(h, xs) if dirn[k] == "high" else auc(xs, h)
                res[f"C10 {k}|{a}"] = round(v, 2); line += f"{v:.2f}".ljust(12)
            print(line)
    json.dump({"rows": rows, "auc": res}, open(V04 / "reports" / "_features.json", "w"), indent=1)

if __name__ == "__main__":
    main()
