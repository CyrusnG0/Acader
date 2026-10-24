"""The outside AI (DeepSeek, via shared/llm.py). Never sees the course archive except what the 'student' pastes.
  python3 scripts/outside.py write  DRAFT.json OUT.txt   # A3/A4: student pastes retrieved passages, asks for an essay, then clicks citations in
  python3 scripts/outside.py bare   OUT.txt              # A6: no archive at all
  python3 scripts/outside.py coach  OUT.txt              # A5: asks which questions to put to a librarian (question only, no corpus)
  python3 scripts/outside.py v4     OUT.txt              # v0.4: the whole archive with passage ids; 500-800 words, inline [DxPy]
  python3 scripts/outside.py revise ESSAY.txt QUESTIONS.txt OUT.txt   # v0.5: essay + a tutor's questions in, revised essay out
  python3 scripts/outside.py answer ESSAY.txt QUESTION.txt OUT.txt    # v0.5: a short first-person answer to one question
"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared"))
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
    elif mode == "v4":
        corpus = json.load(open(Path(__file__).resolve().parents[1] / "data" / "corpus.json"))
        body = "\n\n".join(f"{d['title']} ({d['type']})\n" + "\n".join(f"[{d['id']}p{i+1}] {t}" for i, t in enumerate(d["paras"])) for d in corpus)
        u = (f"Here is the whole course archive, with passage ids:\n\n{body}\n\nWrite me a 500-800 word essay answering: {Q}\n"
             "Cite evidence inline using the passage ids in square brackets, like [D6p2].")
        Path(sys.argv[2]).write_text(llm.chat(SYS, u, max_tokens=1600, temperature=0.7))
    elif mode in ("revise", "answer"):
        essay, ques = Path(sys.argv[2]).read_text(), Path(sys.argv[3]).read_text()
        if mode == "revise":
            corpus = json.load(open(Path(__file__).resolve().parents[1] / "data" / "corpus.json"))
            body = "\n\n".join(f"{d['title']} ({d['type']})\n" + "\n".join(f"[{d['id']}p{i+1}] {t}" for i, t in enumerate(d["paras"])) for d in corpus)
            u = (f"Course archive:\n\n{body}\n\nMy essay:\n\n{essay}\n\nA tutor asked me these questions about it:\n{ques}\n\n"
                 "Rewrite the essay (500-800 words, same question, inline passage ids like [D6p2]) so that the points the tutor asked about are clearly worked out in the text.")
            Path(sys.argv[4]).write_text(llm.chat(SYS, u, max_tokens=1600, temperature=0.7))
        else:
            u = (f"My essay:\n\n{essay}\n\nA tutor asked me: {ques}\n\nWrite my answer in first person, 2 to 4 sentences, in plain student English, "
                 "saying how I arrived at this point.")
            Path(sys.argv[4]).write_text(llm.chat(SYS, u, max_tokens=250, temperature=0.7))
    elif mode == "coach":
        u = (f"My essay question is: \"{Q}\"\nI can ask a librarian bot questions about a sealed archive of course "
             "documents (policy brief, data, interviews, a stakeholder submission, a working paper, comparative cases, "
             "a legal opinion, minutes, an NGO report, news). It answers one passage per question. "
             "List the 10 best specific questions I should ask it, one per line, no numbering, no commentary.")
        Path(sys.argv[2]).write_text(llm.chat(SYS, u, max_tokens=500, temperature=0.7))
    print("writer=" + llm.MODEL)

main()
