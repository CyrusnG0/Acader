"""The outside AI (DeepSeek, via demo/llm.py). Never sees the course archive except what the 'student' pastes.
  python3 scripts/outside.py write  DRAFT.json OUT.txt   # A3/A4: student pastes retrieved passages, asks for an essay, then clicks citations in
  python3 scripts/outside.py bare   OUT.txt              # A6: no archive at all
  python3 scripts/outside.py coach  OUT.txt              # A5: asks which questions to put to a librarian (question only, no corpus)
"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "demo"))
import llm

Q = "Should Hong Kong tighten rent control on subdivided units? Take a position and defend it with evidence from the course archive."
SYS = "You are a helpful writing assistant."

def passages(draft):
    allp = {}
    for d in json.load(open(Path(__file__).resolve().parents[1] / "data" / "corpus.json")):
        for i, t in enumerate(d["paras"]):
            allp[f"{d['id']}p{i+1}"] = t
    seen = []
    for p in draft["retrievals"]:
        if p not in seen: seen.append(p)
    return [(p, allp[p]) for p in seen]

def words(s): return set(w for w in re.findall(r"[a-z]{5,}", s.lower()))

def click_citations(essay, ps, limit=12):
    """Student clicks a hook after the best-matching sentence for each retrieved passage, up to 12 (v0.3: v0.2 capped at 6, which inflated the honest-vs-outsourced orphan gap)."""
    sents = re.split(r"(?<=[.!?])\s+", essay.strip()); used = set(); out = list(sents)
    for pid, text in ps:
        if len(used) >= limit: break
        w = words(text); best, bs = None, 0
        for i, s in enumerate(out):
            if i in used: continue
            sc = len(words(s) & w)
            if sc > bs: best, bs = i, sc
        if best is not None and bs >= 2:
            out[best] = out[best].rstrip() + f" [{pid}]"; used.add(best)
    return " ".join(out)

def main():
    mode = sys.argv[1]
    if mode == "write":
        d = json.load(open(sys.argv[2])); ps = passages(d)
        body = "\n\n".join(f"{t}" for _, t in ps)
        u = f"Here are my course readings:\n\n{body}\n\nWrite me a 500-800 word essay answering: {Q.split(' Take')[0]}"
        essay = llm.chat(SYS, u, max_tokens=1400, temperature=0.7)
        Path(sys.argv[3]).write_text(click_citations(essay, ps))
    elif mode == "bare":
        essay = llm.chat(SYS, f"Write me a 500-800 word essay answering: {Q}", max_tokens=1400, temperature=0.7)
        Path(sys.argv[2]).write_text(essay)
    elif mode == "coach":
        u = (f"My essay question is: \"{Q}\"\nI can ask a librarian bot questions about a sealed archive of course "
             "documents (policy brief, data, interviews, a stakeholder submission, a working paper, comparative cases, "
             "a legal opinion, minutes, an NGO report, news). It answers one passage per question. "
             "List the 10 best specific questions I should ask it, one per line, no numbering, no commentary.")
        Path(sys.argv[2]).write_text(llm.chat(SYS, u, max_tokens=500, temperature=0.7))
    print("writer=" + llm.MODEL)

main()
