"""CLI sub-commands for history retention / pruning."""

from __future__ import annotations

import argparse
from pathlib import Path

from pipewatch.retention import prune_history, prune_all


def _add_subcommands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("prune", help="Prune old history entries")
    p.add_argument(
        "--history-dir",
        default=".pipewatch/history",
        metavar="DIR",
        help="Directory containing *.jsonl history files (default: .pipewatch/history)",
    )
    p.add_argument(
        "--pipeline",
        metavar="NAME",
        help="Prune only this pipeline's history file",
    )
    p.add_argument(
        "--max-age-days",
        type=int,
        metavar="N",
        help="Remove entries older than N days",
    )
    p.add_argument(
        "--max-entries",
        type=int,
        metavar="N",
        help="Keep only the N most recent entries per pipeline",
    )
    p.set_defaults(func=handle_prune)


def handle_prune(args: argparse.Namespace) -> int:
    history_dir = Path(args.history_dir)

    if args.max_age_days is None and args.max_entries is None:
        print("error: at least one of --max-age-days or --max-entries is required")
        return 2

    if args.pipeline:
        hist_file = history_dir / f"{args.pipeline}.jsonl"
        removed = prune_history(
            hist_file,
            max_age_days=args.max_age_days,
            max_entries=args.max_entries,
        )
        print(f"Pruned {removed} record(s) from '{args.pipeline}'.")
    else:
        results = prune_all(
            history_dir,
            max_age_days=args.max_age_days,
            max_entries=args.max_entries,
        )
        total = sum(results.values())
        for name, count in results.items():
            print(f"  {name}: {count} record(s) pruned")
        print(f"Total pruned: {total}")

    return 0
