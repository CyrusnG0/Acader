"""python -m golden actions <id> | show <id|all>   (run with cwd prototype/server)."""
from __future__ import annotations

import sys

import yaml

from .build import build_session
from .project import project, project_compiled
from .script import list_sessions, load_script, main_actions


def _dump(obj) -> str:
    return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True)


def show(session_id: str) -> bool:
    script = load_script(session_id)
    res = build_session(session_id)
    projections = {
        "expected_receipt": project(res.l1, res.compile),
        "expected_compiled_receipt": project_compiled(res.receipt),
    }
    print(f"# {session_id}")
    matched = True
    for name, got in projections.items():
        print(f"# {name}")
        print(_dump(got))
        want = script[name]
        diffs = [k for k in dict.fromkeys([*want, *got]) if want.get(k) != got.get(k)]
        if not diffs:
            print(f"MATCH {name}")
        for k in diffs:
            matched = False
            print(f"DIFF {name}.{k}:\n  expected: {want.get(k)}\n  got:      {got.get(k)}")
    return matched


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[0] == "actions":
        return main_actions(argv[1])
    if len(argv) == 2 and argv[0] == "show":
        matched = True
        for sid in (list_sessions() if argv[1] == "all" else [argv[1]]):
            matched = show(sid) and matched
        return 0 if matched else 1
    print("usage: python -m golden actions <session_id> | show <session_id|all>",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
