"""P0 controls for v0.5 (see PREREG-v0.5.md §A). Writes only to v04/reports-v05/ and v04/judge_packets/.
  python3 v04/controls.py perm            # A.1 permutation tests, no LLM
  python3 v04/controls.py swap            # A.2 trail swap (LLM)
  python3 v04/controls.py essayonly       # A.3 stylometry (+ blind read with --llm)
  python3 v04/controls.py judge-r1 [--smoke] # A.4 J1: run with DEEPSEEK_MODEL=deepseek-reasoner in the environment
  python3 v04/controls.py packets | import   # A.4 J2 (Claude judges)
"""
import itertools, json, random, re, statistics as st, sys
from pathlib import Path
V04 = Path(__file__).resolve().parent
sys.path.insert(0, str(V04))
from score import auc, boot_ci

OUT = V04 / "reports-v05"
CTRL = OUT / "_controls.json"
WRITE_KEYS = ["essay", "citations", "drafts", "struct"]
THINK_KEYS = ["turns", "src_requests", "picks", "unlocked_docs", "read_passages", "counters", "question_kinds"]

def runs():
    return {p.stem: json.load(open(p)) for p in sorted((V04 / "runs").glob("C*.json"))}

def reports():
    return {p.stem: json.load(open(p)) for p in sorted((V04 / "reports").glob("C*.json")) if not p.name.endswith(".audit.json")}

def arm_ids(rs, arm):
    key = lambda i: int(i.split("-")[1])
    return sorted([i for i, r in rs.items() if r["arm"] == arm], key=key)

def save_ctrl(section, data):
    OUT.mkdir(exist_ok=True)
    cur = json.load(open(CTRL)) if CTRL.exists() else {}
    cur[section] = data
    json.dump(cur, open(CTRL, "w"), indent=1)

# ---------- A.1 permutation ----------
def perm_p(h, o, higher_is_honest, nperm=10000, seed=3):
    """One-sided p of the observed AUC (honest side expected on the 'good' side). Exact if C(n,k) <= nperm."""
    stat = (lambda a, b: auc(a, b)) if higher_is_honest else (lambda a, b: auc(b, a))
    obs = stat(h, o)
    pool, k = h + o, len(h)
    idx = range(len(pool))
    combos = itertools.combinations(idx, k)
    from math import comb
    exact = comb(len(pool), k) <= nperm
    if not exact:
        rng = random.Random(seed)
        combos = (tuple(rng.sample(list(idx), k)) for _ in range(nperm))
    vals = []
    for c in combos:
        cs = set(c)
        vals.append(stat([pool[i] for i in c], [pool[i] for i in idx if i not in cs]))
    p = sum(1 for v in vals if v >= obs - 1e-12) / len(vals)
    return obs, p, exact, vals

def smallest_sig_auc(vals):
    s = sorted(set(round(v, 6) for v in vals))
    return next((a for a in s if sum(1 for v in vals if v >= a - 1e-9) / len(vals) <= 0.05), None)

def cmd_perm():
    import features
    rs, rp = runs(), reports()
    f13 = {i: features.f13(rs[i], rp[i]) for i in rs if i in rp}
    comp = {i: rp[i]["composite_nostruct"] for i in rp}
    rows, nullvals = [], None
    def add(label, hon, out, vals, higher):
        nonlocal nullvals
        h = [vals[i] for i in hon if vals.get(i) is not None]; o = [vals[i] for i in out if vals.get(i) is not None]
        if len(h) < 2 or len(o) < 2: return
        a, p, exact, nv = perm_p(h, o, higher)
        nullvals = nv if len(h) == 6 and len(o) == 6 else nullvals
        rows.append({"comparison": label, "n": [len(h), len(o)], "auc": round(a, 3), "p_one_sided": round(p, 4), "exact": exact})
    for a in ["C4", "C5", "C6", "C7", "C8", "C9"]:
        add(f"composite_nostruct C1 vs {a}", arm_ids(rs, "C1"), arm_ids(rs, a), comp, True)
    for h in ["C1", "C10"]:
        for a in ["C6", "C7", "C8", "C9"]:
            add(f"F13 {h} vs {a}", arm_ids(rs, h), arm_ids(rs, a), f13, False)
    out = {"rows": rows, "smallest_auc_p05_6v6": smallest_sig_auc(nullvals) if nullvals else None}
    save_ctrl("perm", out)
    print("comparison".ljust(34), "n".ljust(8), "AUC".ljust(7), "p")
    for r in rows: print(r["comparison"].ljust(34), str(r["n"]).ljust(8), str(r["auc"]).ljust(7), r["p_one_sided"], "exact" if r["exact"] else "")
    print("smallest AUC with p<0.05 at 6 vs 6:", out["smallest_auc_p05_6v6"])

# ---------- A.2 trail swap ----------
def hybrid(i_run, j_run, new_id):
    h = {k: v for k, v in i_run.items() if k not in THINK_KEYS and k not in ("flags",)}
    for k in THINK_KEYS: h[k] = j_run[k]
    h["id"] = new_id
    return h

def deranged_pairs(rs, arm):
    ids = arm_ids(rs, arm)
    return [(ids[k], ids[(k + 1) % len(ids)]) for k in range(len(ids))]

def build_swaps(rs):
    sw = {}
    for arm in ("C1", "C10"):
        for i, j in deranged_pairs(rs, arm):
            sw[f"S1-{i}x{j}"] = (hybrid(rs[i], rs[j], f"S1-{i}x{j}"), i, "S1", arm)
    c1, c8 = arm_ids(rs, "C1"), arm_ids(rs, "C8")
    for e, t in zip(c8, c1):
        sw[f"S2-{e}x{t}"] = (hybrid(rs[e], rs[t], f"S2-{e}x{t}"), e, "S2", "C8")
    for e, t in zip(c1, c8):
        sw[f"S3-{e}x{t}"] = (hybrid(rs[e], rs[t], f"S3-{e}x{t}"), e, "S3", "C1")
    return sw

def cmd_swap():
    import lineage
    rs, rp = runs(), reports()
    (OUT / "swap").mkdir(parents=True, exist_ok=True)
    cur = {"i": None}
    # essay-only inputs are identical to the owner's v0.4 run (same text, temperature 0): reuse them, only the ancestor calls are new
    lineage.get_claims = lambda essay: [{"para": c["para"], "claim": c["claim"]} for c in rp[cur["i"]]["claims"]]
    lineage.cite_check = lambda run: (rp[cur["i"]]["components"]["cite"], rp[cur["i"]]["cites"])
    for name, (h, owner, grp, arm) in build_swaps(rs).items():
        out = OUT / "swap" / f"{name}.json"
        if out.exists(): continue
        cur["i"] = owner
        rep = lineage.report(lineage.strip(h))
        json.dump({"id": name, "group": grp, "essay_owner": owner, "arm": arm, **rep}, open(out, "w"), indent=1)
        print(name, f"composite_nostruct {rep['composite_nostruct']:.1f} claim {rep['components']['claim']:.1f}", flush=True)
    swap_summary()

def swap_summary():
    rs, rp = runs(), reports()
    sw = [json.load(open(p)) for p in sorted((OUT / "swap").glob("*.json"))]
    g = lambda grp: [s for s in sw if s["group"] == grp]
    matched = [rp[i] for a in ("C1", "C10") for i in arm_ids(rs, a)]
    s1 = g("S1")
    res = {}
    for label, f in [("composite_nostruct", lambda r: r["composite_nostruct"]), ("claim", lambda r: r["components"]["claim"])]:
        a, b = [f(r) for r in matched], [f(r) for r in s1]
        lo, hi = boot_ci(a, b)
        res[f"E-A1 {label} matched(C1+C10) vs S1"] = {"auc": round(auc(a, b), 3), "ci": [round(lo, 3), round(hi, 3)]}
        for arm in ("C1", "C10"):
            a1 = [f(rp[i]) for i in arm_ids(rs, arm)]; b1 = [f(r) for r in s1 if r["arm"] == arm]
            res[f"E-A1 {label} {arm} vs its S1"] = {"auc": round(auc(a1, b1), 3)}
    rng = random.Random(11)
    a, b = [r["components"]["claim"] for r in matched], [r["components"]["claim"] for r in s1]
    diffs = sorted(st.mean(rng.choice(a) for _ in a) - st.mean(rng.choice(b) for _ in b) for _ in range(2000))
    res["E-A2 claim drop matched-S1"] = {"mean": round(st.mean(a) - st.mean(b), 1), "ci": [round(diffs[50], 1), round(diffs[1949], 1)]}
    s2 = g("S2")
    res["E-A3 S2 composite_nostruct"] = round(st.mean(r["composite_nostruct"] for r in s2), 1)
    res["E-A3 C8 own composite_nostruct (same essays)"] = round(st.mean(rp[r["essay_owner"]]["composite_nostruct"] for r in s2), 1)
    res["E-A3 S2 claim lineage"] = round(st.mean(r["components"]["claim"] for r in s2), 1)
    res["S3 composite_nostruct (honest essay, relay trail)"] = round(st.mean(r["composite_nostruct"] for r in g("S3")), 1)
    res["S3 claim"] = round(st.mean(r["components"]["claim"] for r in g("S3")), 1)
    res["matched composite_nostruct mean"] = round(st.mean(r["composite_nostruct"] for r in matched), 1)
    res["S1 composite_nostruct mean"] = round(st.mean(r["composite_nostruct"] for r in s1), 1)
    res["matched claim mean"] = round(st.mean(a), 1); res["S1 claim mean"] = round(st.mean(b), 1)
    save_ctrl("swap", res)
    for k, v in res.items(): print(k.ljust(52), v)

# ---------- A.3 essay-only ----------
def sents(t): return [s for s in re.split(r"(?<=[.!?])\s+", re.sub(r"\[D\d+p\d+\]", "", t).strip()) if s]
def words(t): return re.findall(r"[a-z0-9']+", t.lower())

STYLO = {
    "mean sentence length": lambda r: st.mean(len(words(s)) for s in sents(r["essay"])),
    "type-token ratio (first 400w)": lambda r: len(set(words(r["essay"])[:400])) / max(1, len(words(r["essay"])[:400])),
    "citations per 100 words": lambda r: 100 * len(r["citations"]) / max(1, len(words(r["essay"]))),
    "share of sentences with a number": lambda r: sum(1 for s in sents(r["essay"]) if re.search(r"\d", s)) / max(1, len(sents(r["essay"]))),
    "mean paragraph length": lambda r: st.mean(len(words(p)) for p in re.split(r"\n\s*\n", r["essay"].strip()) if p.strip()),
}

def blind_read(essay):
    import llmx
    sysmsg = ("You read an essay and judge how it was produced. Give a number 0 to 100: 0 means it was produced in one pass by a writing tool, "
              "100 means it was developed step by step by a student who researched it. Return json {\"process\": number}. Output only json.")
    r = llmx.jchat(sysmsg, essay, tag="blindread", max_tokens=60)
    return float(r.get("process", 50)) if isinstance(r, dict) else 50.0

def cmd_essayonly():
    rs = runs()
    vals = {k: {i: fn(r) for i, r in rs.items()} for k, fn in STYLO.items()}
    if "--llm" in sys.argv:
        cache = OUT / "_blindread.json"
        done = json.load(open(cache)) if cache.exists() else {}
        for i, r in rs.items():
            if i not in done:
                done[i] = blind_read(r["essay"]); json.dump(done, open(cache, "w"))
        vals["blind LLM read (process)"] = done
    arms = sorted({r["arm"] for r in rs.values()} - {"C1"}, key=lambda a: int(a[1:]))
    res = {}
    print("AUC of C1 above arm (0.50 = no separation; <0.20 or >0.80 = essay alone separates)")
    print("feature".ljust(34) + "".join(a.ljust(7) for a in arms))
    for k, v in vals.items():
        c1 = [v[i] for i in arm_ids(rs, "C1")]
        row = {a: round(auc(c1, [v[i] for i in arm_ids(rs, a)]), 2) for a in arms}
        res[k] = row
        print(k.ljust(34) + "".join(str(row[a]).ljust(7) for a in arms))
    save_ctrl("essayonly", res)

# ---------- A.4 J1 ----------
def cmd_judge_r1():
    import lineage, llm, llmx
    print("model:", llm.MODEL)
    _chat = llmx.chat  # reasoner spends tokens on hidden reasoning: larger budget, no json mode (PREREG-v0.5 §C-1)
    llmx.chat = lambda s, u, *, tag, json_mode=False, max_tokens=900, temperature=0.4: _chat(s, u, tag=tag, json_mode=False, max_tokens=max(max_tokens * 8, 24000), temperature=temperature)
    rs = runs()
    out_dir = OUT / "judge-r1"; out_dir.mkdir(parents=True, exist_ok=True)
    ids = [next(iter(rs))] if "--smoke" in sys.argv else list(rs)
    for i in ids:
        out = out_dir / f"{i}.json"
        if out.exists() and "--smoke" not in sys.argv: continue
        run = lineage.strip(rs[i]); sts = lineage.student_statements(run["turns"])
        score, claims = lineage.claim_lineage(run, sts)
        json.dump({"id": i, "arm": rs[i]["arm"], "model": llm.MODEL, "claim": score, "claims": claims}, open(out, "w"), indent=1)
        print(i, f"claim {score:.1f} ({len(claims)} claims)", flush=True)

# ---------- A.4 J2 packets ----------
def cmd_packets():
    import lineage
    rs, rp = runs(), reports()
    pd = V04 / "judge_packets"; pd.mkdir(exist_ok=True)
    rng = random.Random(7)
    chosen = []
    for arm in ("C1", "C10", "C4", "C6", "C8", "C9"):
        chosen += rng.sample(arm_ids(rs, arm), 4)
    rng.shuffle(chosen)
    key = {}
    for n, i in enumerate(chosen, 1):
        pid = f"P{n:02d}"
        run = lineage.strip(rs[i]); sts = lineage.student_statements(run["turns"])
        pkt = {"packet": pid, "claims": [{"n": k + 1, "claim": c["claim"]} for k, c in enumerate(rp[i]["claims"])],
               "statements": lineage.fmt_statements(sts)}
        json.dump(pkt, open(pd / f"{pid}.json", "w"), indent=1)
        key[pid] = i
    json.dump(key, open(pd / "_key.json", "w"), indent=1)
    print("wrote", len(chosen), "packets")

def cmd_import():
    pd = V04 / "judge_packets"
    key = json.load(open(pd / "_key.json")); rs, rp = runs(), reports()
    valid_by = {}
    import lineage
    out = {}
    for pid, i in key.items():
        ap = pd / f"{pid}.answer.json"
        if not ap.exists(): print("missing answer", pid); continue
        ans = json.load(open(ap)); res = {int(x["n"]): x.get("turn") for x in ans.get("results", [])}
        sts = lineage.student_statements(rs[i]["turns"]); valid = {s["i"] for s in sts if s["label"] != "pasted"}
        n = len(rp[i]["claims"])
        got = [res.get(k) in valid for k in range(1, n + 1)]
        out[i] = 100.0 * sum(got) / n
    json.dump(out, open(OUT / "judge-j2.json", "w"), indent=1)
    print(len(out), "packets scored")

def cmd_judge_summary():
    rs, rp = runs(), reports()
    res = {}
    def spearman(a, b):
        import features
        return features.spearman(a, b)
    for name, src in [("J1 deepseek-reasoner", {p.stem: json.load(open(p))["claim"] for p in (OUT / "judge-r1").glob("C*.json")}),
                      ("J2 Claude", json.load(open(OUT / "judge-j2.json")) if (OUT / "judge-j2.json").exists() else {})]:
        ids = sorted(src)
        if len(ids) < 3: continue
        base = [rp[i]["components"]["claim"] for i in ids]; alt = [src[i] for i in ids]
        row = {"n": len(ids), "spearman_vs_v04": round(spearman(base, alt), 3)}
        hon = [i for i in ids if rs[i]["arm"] in ("C1", "C10")]; out = [i for i in ids if rs[i]["arm"] in ("C6", "C8", "C9")]
        if hon and out:
            row["AUC honest vs relay (alt judge)"] = round(auc([src[i] for i in hon], [src[i] for i in out]), 3)
            row["AUC honest vs relay (v0.4 judge, same runs)"] = round(auc([rp[i]["components"]["claim"] for i in hon], [rp[i]["components"]["claim"] for i in out]), 3)
        res[name] = row
    save_ctrl("judge", res)
    for k, v in res.items(): print(k, v)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    fn = {"perm": cmd_perm, "swap": cmd_swap, "swap-summary": swap_summary, "essayonly": cmd_essayonly, "judge-r1": cmd_judge_r1,
          "packets": cmd_packets, "import": cmd_import, "judge-summary": cmd_judge_summary}.get(cmd)
    if not fn: print(__doc__); sys.exit(1)
    fn()
