"""CLI subcommand: pipewatch metrics."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pipewatch.metrics import compute_metrics, format_metrics_text


def _add_subcommands(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("metrics", help="Show runtime metrics for a pipeline")
    p.add_argument("pipeline", help="Pipeline name")
    p.add_argument(
        "--history",
        default="pipewatch_history.jsonl",
        metavar="FILE",
        help="History file (default: pipewatch_history.jsonl)",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    p.set_defaults(func=handle_metrics)


def handle_metrics(args: argparse.Namespace) -> int:
    hist = args.history
    if not Path(hist).exists():
        print(f"[error] history file not found: {hist}", file=sys.stderr)
        return 2

    m = compute_metrics(hist, args.pipeline)

    if args.json:
        import json
        data = {
            "pipeline": m.name,
            "total_runs": m.total_runs,
            "success_count": m.success_count,
            "failure_count": m.failure_count,
            "success_rate": m.success_rate,
            "avg_duration_s": m.avg_duration_s,
            "min_duration_s": m.min_duration_s,
            "max_duration_s": m.max_duration_s,
        }
        print(json.dumps(data, indent=2))
    else:
        print(format_metrics_text(m))

    return 0
