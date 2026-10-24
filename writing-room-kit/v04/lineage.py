"""The coherence report. python3 v04/lineage.py RUN.json [RUN.json ...] [--force]
Every claim, source and change in the final work should have an earlier ancestor in the Room.
Gaps are phrased as questions, never verdicts. `arm` and `id` are stripped before any LLM call."""
import difflib, json, re, sys
from pathlib import Path
V04 = Path(__file__).resolve().parent
sys.path.insert(0, str(V04))
import llmx

W = {"claim": 0.35, "source": 0.20, "cite": 0.15, "change": 0.15, "struct": 0.15}
KEY_PATH = V04.parent / "data" / "answer-key.json"
CITE = re.compile(r"\[(D\d+p\d+)\]")

def answer_key():
    return json.load(open(KEY_PATH)) if KEY_PATH.exists() else {}

def passages():
    return {f"{d['id']}p{i+1}": t for d in json.load(open(V04.parent / "data" / "corpus.json")) for i, t in enumerate(d["paras"])}

def paragraphs(text):
    ps = [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    if len(ps) <= 1:
        ps = [p.strip() for p in text.strip().split("\n") if p.strip()]
    return ps

def sentences(text):
    return [s for s in re.split(r"(?<=[.!?\]])\s+", text.strip()) if s]

def student_statements(turns):
    """Typed student statements the judge may use as ancestors (own words only)."""
    out = []
    for t in turns:
        if t["who"] != "student" or t["kind"] not in ("say", "confident", "pick", "answer"): continue
        label = "pick reason" if t["kind"] == "pick" else ("answer to a question" if t["kind"] == "answer" else ("pasted" if t.get("paste") else "typed"))
        out.append({"i": t["i"], "label": label, "text": t["text"]})
    return out

def fmt_statements(sts):
    return "\n".join(f"[{s['i']}] ({s['label']}) {s['text']}" for s in sts) or "(none)"

# ---------- pure components ----------
def source_lineage(run):
    cited = {c["pid"].split("p")[0] for c in run["citations"]}
    picked = {d for p in run["picks"] for d in p["docs"] if len(p["reason"].split()) >= 3}
    if not cited: return 0.0, []
    missing = sorted(cited - picked)
    return 100.0 * len(cited & picked) / len(cited), missing

def struct_score(run):
    st = run["struct"]
    if st["kind"] in ("typed", "retyped"): return 100.0
    n = max(1, len(run["essay"]))
    return 100.0 * (1 - min(1.0, st["paste_chars"] / n))

def changed_paragraphs(prev, cur):
    """Paragraphs of `cur` that are new, or whose best match in `prev` has difflib ratio < 0.5."""
    pp = paragraphs(prev) if prev else []
    out = []
    for n, para in enumerate(paragraphs(cur), 1):
        best = max((difflib.SequenceMatcher(None, para, q).ratio() for q in pp), default=0.0)
        if best < 0.5: out.append({"para": n, "text": para})
    return out

def snapshots(run):
    """[(text, start_turn, end_turn)]: windows of student turns between consecutive snapshots."""
    snaps = [("", 0)] + [(d["text"], d["turn"]) for d in run["drafts"]]
    last = (run["turns"][-1]["i"] + 1) if run["turns"] else 0
    snaps.append((run["essay"], last))
    out = []
    for k in range(1, len(snaps)):
        out.append((snaps[k - 1][0], snaps[k][0], snaps[k - 1][1], snaps[k][1]))
    return out

# ---------- judged components ----------
def get_claims(essay):
    sysmsg = ("You read an essay and list its distinct claims (assertions the author makes, including evidence-based ones). "
              "Return json {\"claims\":[{\"para\":paragraph number starting at 1,\"claim\":\"one short sentence\"}]} with 8 to 20 claims. "
              "Output only json.")
    numbered = "\n\n".join(f"Paragraph {i}:\n{p}" for i, p in enumerate(paragraphs(essay), 1))
    r = llmx.jchat(sysmsg, numbered, tag="claims", max_tokens=1500)
    cl = r.get("claims", r) if isinstance(r, dict) else r
    return [c for c in cl if isinstance(c, dict) and c.get("claim")]

def claim_lineage(run, sts):
    claims = get_claims(run["essay"])
    valid = {s["i"] for s in sts if s["label"] != "pasted"}
    sysmsg = ("You check where each claim in a finished essay first came from in the author's earlier work. "
              "You get numbered student statements [turn] (label) text, and numbered claims. For each claim, give the EARLIEST turn where the student "
              "themselves states, chooses or defends that point in their own words, or null if none. A statement labelled 'pasted' never counts. "
              "Agreeing with something an assistant said counts only if the student restates the point. A loose topical mention is not enough; the point itself must be there. "
              "Return json {\"results\":[{\"n\":claim number,\"turn\":turn number or null}]}. Output only json.")
    anc = {}
    for b in range(0, len(claims), 10):
        chunk = claims[b:b + 10]
        user = ("Student statements:\n" + fmt_statements(sts) + "\n\nClaims:\n" +
                "\n".join(f"{b + k + 1}. {c['claim']}" for k, c in enumerate(chunk)))
        r = llmx.jchat(sysmsg, user, tag="ancestor", max_tokens=700)
        for item in (r.get("results", []) if isinstance(r, dict) else []):
            try: anc[int(item["n"])] = item.get("turn")
            except (KeyError, TypeError, ValueError): pass
    res = []
    for k, c in enumerate(claims, 1):
        t = anc.get(k)
        res.append({"para": c.get("para"), "claim": c["claim"], "ancestor": t if t in valid else None})
    score = 100.0 * sum(1 for r in res if r["ancestor"] is not None) / len(res) if res else 0.0
    return score, res

def cite_check(run):
    key, ps = answer_key(), passages()
    sysmsg = ("You check whether a cited passage supports the sentence that cites it. You get the sentence, the passage, and a list of facts the passage supports. "
              "Return json {\"supports\":\"yes\"|\"partial\"|\"no\"}: yes = the sentence's factual content is in the passage; partial = some of it, or it overstates; no = not supported. Output only json.")
    essay = run["essay"]
    out = []
    for c in run["citations"]:
        sent = next((s for s in sentences(essay) if c["pid"] in s and essay.find(s) <= c["pos"] < essay.find(s) + len(s)), None)
        if sent is None: sent = essay[max(0, c["pos"] - 200):c["pos"] + 10]
        user = f"Sentence: {sent}\n\nPassage {c['pid']}: {ps.get(c['pid'], '(no such passage)')}\n\nFacts: {json.dumps(key.get(c['pid'], []))}"
        v = llmx.jchat(sysmsg, user, tag="cite", max_tokens=60).get("supports", "no")
        out.append({"pid": c["pid"], "sentence": sent, "supports": v if v in ("yes", "partial", "no") else "no"})
    pts = {"yes": 1.0, "partial": 0.5, "no": 0.0}
    score = 100.0 * sum(pts[o["supports"]] for o in out) / len(out) if out else 0.0
    return score, out

def change_lineage(run, sts):
    sysmsg = ("You check whether changes to a draft were talked about. You get numbered changed paragraphs and the student's typed statements made between two saves of the draft. "
              "For each paragraph say discussed=true only if one of those statements discusses that paragraph's main point (the student states, weighs or explains it). Pasted statements do not count. "
              "Return json {\"results\":[{\"n\":paragraph number,\"discussed\":true|false}]}. Output only json.")
    detail = []
    total = disc = 0
    for prev, cur, t0, t1 in snapshots(run):
        ch = changed_paragraphs(prev, cur)
        if not ch: continue
        win = [s for s in sts if t0 <= s["i"] < t1 and s["label"] != "pasted"]
        got = {}
        if win:
            user = "Statements between the two saves:\n" + fmt_statements(win) + "\n\nChanged paragraphs:\n" + "\n\n".join(f"{c['para']}. {c['text'][:700]}" for c in ch[:12])
            r = llmx.jchat(sysmsg, user, tag="change", max_tokens=500)
            for item in (r.get("results", []) if isinstance(r, dict) else []):
                try: got[int(item["n"])] = bool(item.get("discussed"))
                except (KeyError, TypeError, ValueError): pass
        for c in ch[:12]:
            ok = got.get(c["para"], False)
            total += 1; disc += int(ok)
            detail.append({"para": c["para"], "window": [t0, t1], "discussed": ok})
    return (100.0 * disc / total if total else 100.0), detail

# ---------- report ----------
def composite(c, with_struct=True):
    keys = list(W) if with_struct else [k for k in W if k != "struct"]
    return sum(W[k] * c[k] for k in keys) / sum(W[k] for k in keys)

def report(run):
    sts = student_statements(run["turns"])
    cs, claims = claim_lineage(run, sts)
    ss, missing = source_lineage(run)
    ks, cites = cite_check(run)
    hs, changes = change_lineage(run, sts)
    st = struct_score(run)
    comp = {"claim": cs, "source": ss, "cite": ks, "change": hs, "struct": st}
    mm = []
    for c in claims:
        if c["ancestor"] is None:
            mm.append(f"Paragraph {c['para']} says: \"{c['claim']}\". This point doesn't appear earlier in your work in the Room. Where did it come from?")
    for d in missing:
        mm.append(f"You cite {d}, but it wasn't chosen with a reason in the Room. How did you come to use it?")
    for c in cites:
        if c["supports"] != "yes":
            mm.append(f"The sentence \"{c['sentence'][:160]}\" cites {c['pid']}. Does that passage say this? Please look at it again with us.")
    for c in changes:
        if not c["discussed"]:
            mm.append(f"Paragraph {c['para']} is new or changed between saves, and that change isn't discussed in the Room. What made you write or change it?")
    if run["struct"]["kind"] == "pasted":
        mm.append("Most of the text arrived as a paste. Can you walk us through it in your own words?")
    qk = {}
    for q in run["question_kinds"]: qk[q["kind"]] = qk.get(q["kind"], 0) + 1
    return {"components": comp, "composite": composite(comp), "composite_nostruct": composite(comp, False),
            "mismatches": mm, "claims": claims, "cites": cites, "changes": changes, "sources_unpicked": missing,
            "inputs": {"write_requests": run["counters"]["write_requests"], "question_kinds": qk,
                       "served_after_cap": sum(1 for r in run["src_requests"] if r.get("served_after_cap"))}}

def strip(run):
    """What the judge may see: no arm, no id."""
    return {k: v for k, v in run.items() if k not in ("arm", "id", "flags")}

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    (V04 / "reports").mkdir(exist_ok=True)
    for p in args:
        run = json.load(open(p))
        out = V04 / "reports" / f"{run['id']}.json"
        if out.exists() and not force: print("skip", run["id"]); continue
        rep = report(strip(run))
        rep = {"id": run["id"], "arm": run["arm"], **rep}
        json.dump(rep, open(out, "w"), indent=1)
        print(f"{run['id']}: composite {rep['composite']:.1f} nostruct {rep['composite_nostruct']:.1f} ({len(rep['mismatches'])} questions)")

if __name__ == "__main__":
    main()
