"""CLI subcommands for managing per-pipeline alert throttle state."""
from __future__ import annotations

import argparse
import sys

from pipewatch.throttle import is_throttled, record_alert, clear_throttle


def _add_subcommands(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("throttle", help="Manage alert throttle state")
    sub = p.add_subparsers(dest="throttle_cmd", required=True)

    chk = sub.add_parser("check", help="Check if a pipeline is currently throttled")
    chk.add_argument("pipeline", help="Pipeline name")
    chk.add_argument("--window", type=int, default=300, metavar="SECS",
                     help="Throttle window in seconds (default 300)")
    chk.add_argument("--state-dir", default=".", metavar="DIR")

    rec = sub.add_parser("record", help="Record that an alert was sent for a pipeline")
    rec.add_argument("pipeline", help="Pipeline name")
    rec.add_argument("--state-dir", default=".", metavar="DIR")

    clr = sub.add_parser("clear", help="Clear throttle state for a pipeline")
    clr.add_argument("pipeline", help="Pipeline name")
    clr.add_argument("--state-dir", default=".", metavar="DIR")


def handle_throttle(args: argparse.Namespace) -> int:
    cmd = args.throttle_cmd
    if cmd == "check":
        throttled = is_throttled(args.pipeline, args.window, state_dir=args.state_dir)
        status = "throttled" if throttled else "not throttled"
        print(f"{args.pipeline}: {status}")
        return 0
    if cmd == "record":
        record_alert(args.pipeline, state_dir=args.state_dir)
        print(f"Recorded alert for '{args.pipeline}'.")
        return 0
    if cmd == "clear":
        clear_throttle(args.pipeline, state_dir=args.state_dir)
        print(f"Cleared throttle state for '{args.pipeline}'.")
        return 0
    print(f"Unknown throttle subcommand: {cmd}", file=sys.stderr)
    return 2
