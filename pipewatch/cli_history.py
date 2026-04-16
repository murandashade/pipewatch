"""CLI sub-commands for inspecting run history."""
from __future__ import annotations

import argparse
import json
import sys

from pipewatch.history import load_history, last_failure, failure_streak, DEFAULT_HISTORY_FILE


def _add_subcommands(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    hist = subparsers.add_parser("history", help="Inspect pipeline run history")
    hist_sub = hist.add_subparsers(dest="history_cmd", required=True)

    show = hist_sub.add_parser("show", help="Print history entries as JSON")
    show.add_argument("--pipeline", "-p", default=None, help="Filter by pipeline name")
    show.add_argument("--file", default=DEFAULT_HISTORY_FILE, help="History file path")
    show.add_argument("--last", type=int, default=None, metavar="N", help="Show last N entries")

    streak = hist_sub.add_parser("streak", help="Show failure streak for a pipeline")
    streak.add_argument("pipeline", help="Pipeline name")
    streak.add_argument("--file", default=DEFAULT_HISTORY_FILE)


def handle_history(args: argparse.Namespace) -> int:
    """Dispatch history sub-commands; returns an exit code."""
    if args.history_cmd == "show":
        entries = load_history(args.file)
        if args.pipeline:
            entries = [e for e in entries if e["pipeline"] == args.pipeline]
        if args.last is not None:
            entries = entries[-args.last :]
        print(json.dumps(entries, indent=2))
        return 0

    if args.history_cmd == "streak":
        streak = failure_streak(args.pipeline, args.file)
        last = last_failure(args.pipeline, args.file)
        print(f"Pipeline '{args.pipeline}' failure streak: {streak}")
        if last:
            print(f"Last failure at {last['timestamp']} (exit {last['exit_code']})")
        return 0

    print(f"Unknown history command: {args.history_cmd}", file=sys.stderr)
    return 1
