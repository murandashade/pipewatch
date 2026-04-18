"""CLI subcommands for exporting pipeline history."""
from __future__ import annotations

import argparse
import sys

from pipewatch.export import export_csv, export_json

_DEFAULT_HISTORY = "pipewatch_history.jsonl"


def _add_subcommands(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("export", help="Export pipeline run history")
    p.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        dest="fmt",
        help="Output format (default: json)",
    )
    p.add_argument("--pipeline", default=None, help="Filter to a single pipeline name")
    p.add_argument(
        "--history-file",
        default=_DEFAULT_HISTORY,
        help="Path to history file",
    )
    p.add_argument(
        "--output",
        default=None,
        help="Write to file instead of stdout",
    )
    p.set_defaults(func=handle_export)


def handle_export(args: argparse.Namespace) -> int:
    try:
        if args.fmt == "csv":
            data = export_csv(args.history_file, args.pipeline)
        else:
            data = export_json(args.history_file, args.pipeline)
    except FileNotFoundError:
        print(f"History file not found: {args.history_file}", file=sys.stderr)
        return 2

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(data)
        print(f"Exported to {args.output}")
    else:
        print(data)
    return 0
