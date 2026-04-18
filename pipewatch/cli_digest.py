"""CLI subcommand: digest — show a summary of recent pipeline runs."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone, timedelta

from pipewatch.digest import build_digest, format_digest_text


def _add_subcommands(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("digest", help="Show a digest of recent pipeline activity")
    p.add_argument(
        "--history-file",
        default=".pipewatch_history.jsonl",
        help="Path to history file (default: .pipewatch_history.jsonl)",
    )
    p.add_argument(
        "--since-hours",
        type=float,
        default=24.0,
        metavar="HOURS",
        help="Only include runs from the last N hours (default: 24)",
    )
    p.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output digest as JSON",
    )
    p.set_defaults(func=handle_digest)


def handle_digest(args: argparse.Namespace) -> int:
    since: datetime | None = None
    if args.since_hours is not None:
        since = datetime.now(timezone.utc) - timedelta(hours=args.since_hours)

    try:
        digest = build_digest(args.history_file, since=since)
    except FileNotFoundError:
        print(f"History file not found: {args.history_file}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(
            {
                "total": digest.total,
                "success": digest.success,
                "failure": digest.failure,
                "by_pipeline": {
                    name: {"total": s.total, "success": s.success, "failure": s.failure}
                    for name, s in digest.by_pipeline.items()
                },
            },
            indent=2,
        ))
    else:
        print(format_digest_text(digest))

    return 0
