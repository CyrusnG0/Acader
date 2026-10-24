import argparse
import json
import sys


def _verify(args) -> int:
    from engine.events import verify

    with open(args.log, encoding="utf-8") as f:
        events = [json.loads(line) for line in f if line.strip()]
    receipt = artifacts = None
    if args.receipt:
        with open(args.receipt, encoding="utf-8") as f:
            receipt = json.load(f)
    if args.artifacts:
        with open(args.artifacts, encoding="utf-8") as f:
            artifacts = json.load(f)
    result = verify(events, args.seal, receipt=receipt, artifacts=artifacts)
    if result.ok:
        print(f"ok: record unchanged up to the seal (seq {result.seal_seq})")
        return 0
    for p in result.problems:
        print(p, file=sys.stderr)
    return 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="engine")
    sub = parser.add_subparsers(dest="cmd", required=True)
    compile_p = sub.add_parser("compile")
    compile_p.add_argument("log")
    verify_p = sub.add_parser("verify", help="check a log (JSON lines) against its seal hash")
    verify_p.add_argument("log")
    verify_p.add_argument("seal")
    verify_p.add_argument("--receipt")
    verify_p.add_argument("--artifacts")
    args = parser.parse_args(argv)
    if args.cmd == "verify":
        return _verify(args)
    print("engine compile: not implemented yet", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
