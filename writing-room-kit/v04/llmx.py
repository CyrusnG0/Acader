"""LLM wrapper for v0.4. Live: shared/llm.py (DeepSeek). ROOM_LLM=stub: deterministic canned output (tests).
Call metadata (never prompt text, never the key) is appended to v04/_calls.jsonl."""
import json, os, re, sys, time
from pathlib import Path

V04 = Path(__file__).resolve().parent
sys.path.insert(0, str(V04.parents[1] / "shared"))

CAPTURED = []      # stub mode only: list of {tag, system, user}
HANDLERS = {}      # stub mode only: tag -> fn(system, user) -> str   (tests override)

def stub_mode():
    return os.environ.get("ROOM_LLM", "") == "stub"

def _default_stub(tag, system, user):
    if tag == "route":
        t = user.lower()
        intent = "other"
        for key, it in [("source", "source_request"), ("write", "write_request"), ("argue", "argument_request"),
                        ("structure", "structure_request"), ("summar", "summary_request"),
                        ("counter", "counter_request"), ("i think", "claim_statement")]:
            if key in t: intent = it; break
        return json.dumps({"intent": intent, "question_kind": "own_thinking"})
    if tag == "src_pick":
        return json.dumps({"need_clear": True, "pick": ["D1", "D2", "D3", "D4", "D5"]})
    if tag == "src_describe":
        return json.dumps({f"D{i}": f"stub description {i}" for i in range(1, 13)})
    if tag == "src_clarify": return "What should a source here show, and for which claim?"
    if tag in ("claims",): return json.dumps({"claims": [{"para": 1, "claim": "stub claim"}]})
    if tag == "ancestor": return json.dumps({"results": []})
    if tag == "cite": return json.dumps({"supports": "yes"})
    if tag == "change": return json.dumps({"results": []})
    if tag == "law1": return json.dumps({"violation": False, "quote": ""})
    if tag == "key": return json.dumps({"facts": ["stub fact"]})
    if tag == "derive": return json.dumps({"units": []})
    if tag == "derive_refine": return json.dumps({"relation": "same"})
    if tag == "relay_write": return "Stub essay about rent [D1p1]."
    if tag == "write": return "What is your idea for this paragraph? One line is enough."
    return f"[stub:{tag}] ok."

def log_call(tag, **meta):
    """Call metadata only (never prompt text, never the key). `run` comes from ROOM_RUN_ID, for effort accounting."""
    try:
        with open(V04 / "_calls.jsonl", "a") as f:
            f.write(json.dumps({"tag": tag, "run": os.environ.get("ROOM_RUN_ID", ""), **meta}) + "\n")
    except OSError:
        pass

def chat(system, user, *, tag, json_mode=False, max_tokens=900, temperature=0.4):
    if stub_mode():
        CAPTURED.append({"tag": tag, "system": system, "user": user})
        fn = HANDLERS.get(tag)
        return fn(system, user) if fn else _default_stub(tag, system, user)
    import llm
    t0 = time.time()
    out = llm.chat(system, user, json_mode=json_mode, max_tokens=max_tokens, temperature=temperature)
    log_call(tag, ts=round(t0), model=llm.MODEL, prompt_chars=len(system) + len(user), reply_chars=len(out))
    return out

def jchat(system, user, *, tag, max_tokens=900, temperature=0.0):
    """json call; one retry on parse failure."""
    last = None
    for _ in range(2):
        raw = chat(system, user, tag=tag, json_mode=True, max_tokens=max_tokens, temperature=temperature)
        try:
            if stub_mode(): return json.loads(raw)
            import llm
            return llm.parse_json(raw)
        except Exception as e:  # noqa
            last = e
    raise RuntimeError(f"bad json from {tag}: {type(last).__name__}")
