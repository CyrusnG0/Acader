"""python -m golden actions <id> | show <id|all>   (run with cwd prototype/server)."""
from __future__ import annotations

import sys

import yaml

from .build import build_session
from .project import project
from .script import list_sessions, load_script, main_actions


def _dump(obj) -> str:
    return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True)


def show(session_id: str) -> None:
    script = load_script(session_id)
    res = build_session(session_id)
    got = project(res.l1, res.compile)
    print(f"# {session_id}")
    print(_dump(got))
    want = script["expected_receipt"]
    diffs = [k for k in dict.fromkeys([*want, *got]) if want.get(k) != got.get(k)]
    if not diffs:
        print("MATCH")
    for k in diffs:
        print(f"DIFF {k}:\n  expected: {want.get(k)}\n  got:      {got.get(k)}")


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[0] == "actions":
        return main_actions(argv[1])
    if len(argv) == 2 and argv[0] == "show":
        for sid in (list_sessions() if argv[1] == "all" else [argv[1]]):
            show(sid)
        return 0
    print("usage: python -m golden actions <session_id> | show <session_id|all>",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
