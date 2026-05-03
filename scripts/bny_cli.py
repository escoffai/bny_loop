"""Minimal ``bny`` CLI placeholder.

Today this only proxies a smoke simulation. Phase 3 wires it to the API
gateway via ``httpx``.
"""

from __future__ import annotations

import argparse

from scripts.sim_smoke import main as sim_smoke_main


def main() -> int:
    parser = argparse.ArgumentParser(prog="bny", description="BNY LOOP CLI (placeholder).")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("simulate", help="Run a local smoke simulation against the reference catalog.")
    args = parser.parse_args()

    if args.cmd == "simulate":
        return sim_smoke_main()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
