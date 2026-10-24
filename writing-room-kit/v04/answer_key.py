"""Builds data/answer-key.json: atomic facts each passage supports (human-readable, spot-checked at gate 1)."""
import json, sys
from pathlib import Path
V04 = Path(__file__).resolve().parent
sys.path.insert(0, str(V04))
import llmx, room

def main():
    sysmsg = ("List the 1 to 4 atomic facts this passage supports (numbers, names, dates, claims), each a short plain sentence that stays within what the passage says. "
              "Return json {\"facts\":[...]}. Output only json.")
    key = {}
    for pid, text in room.PASSAGES.items():
        key[pid] = llmx.jchat(sysmsg, f"Passage {pid}: {text}", tag="key", max_tokens=300).get("facts", [])
        print(pid, len(key[pid]))
    out = V04.parent / "data" / "answer-key.json"
    json.dump(key, open(out, "w"), indent=1, ensure_ascii=False)
    print("wrote", out)

if __name__ == "__main__":
    main()
