"""The check -> questions loop used by the adaptive attackers (arms C13, C14). The same call a student can make: room.py check.
  check_round(session, essay_text) -> list of Coach questions (never a score)"""
import sys
from pathlib import Path
V04 = Path(__file__).resolve().parent
sys.path.insert(0, str(V04))
import room

def check_round(s, essay_text):
    f = room.sessions_dir() / f"{s['name']}-check{len(s.get('checks', [])) + 1}.txt"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(essay_text)
    return room.cmd_check(s, str(f))
