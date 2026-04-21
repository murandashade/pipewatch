"""CLI sub-command: pipewatch status"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pipewatch.config import load_config, validate_config
from pipewatch.pipeline_status import all_pipeline_statuses, format_status_text


_DEFAULT_HISTORY = Path("pipewatch_history.jsonl")
_DEFAULT_MUTE = Path(".pipewatch_mute.json")
_DEFAULT_BASELINE = Path(".pipewatch_baseline.json")


def _add_subcommands(subparsers) -> None:
    p = subparsers.add_parser("status", help="Show live status for all pipelines")
    p.add_argument("--config", default="pipewatch.json", help="Config file")
    p.add_argument("--history-file", default=str(_DEFAULT_HISTORY))
    p.add_argument("--mute-file", default=str(_DEFAULT_MUTE))
    p.add_argument("--baseline-file", default=str(_DEFAULT_BASELINE))
    p.add_argument("--json", action="store_true", help="Output as JSON")
    p.add_argument("--pipeline", default=None, help="Filter to a single pipeline")
    p.set_defaults(func=handle_status)


def handle_status(args) -> int:
    try:
        cfg = load_config(args.config)
        validate_config(cfg)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    names = [p.name for p in cfg.pipelines]
    if args.pipeline:
        if args.pipeline not in names:
            print(f"error: unknown pipeline '{args.pipeline}'", file=sys.stderr)
            return 2
        names = [args.pipeline]

    statuses = all_pipeline_statuses(
        names,
        history_file=Path(args.history_file),
        mute_file=Path(args.mute_file),
        baseline_file=Path(args.baseline_file),
    )

    if args.json:
        out = [
            {
                "name": s.name,
                "last_run": s.last_run,
                "last_outcome": s.last_outcome,
                "failure_streak": s.failure_streak,
                "muted": s.muted,
                "baseline_seconds": s.baseline_seconds,
                "last_duration": s.last_duration,
            }
            for s in statuses
        ]
        print(json.dumps(out, indent=2))
    else:
        print(format_status_text(statuses))

    return 0
