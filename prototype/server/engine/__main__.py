import argparse
import sys


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="engine")
    sub = parser.add_subparsers(dest="cmd", required=True)
    compile_p = sub.add_parser("compile")
    compile_p.add_argument("log")
    parser.parse_args(argv)
    print("engine compile: not implemented yet", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
