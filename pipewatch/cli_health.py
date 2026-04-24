"""CLI sub-commands for pipeline health scoring."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from pipewatch.config import load_config, validate_config
from pipewatch.pipeline_health import all_health_scores, compute_health, format_health_text


def _add_subcommands(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("health", help="Show pipeline health scores")
    p.add_argument("--config", default="pipewatch.json", metavar="FILE")
    p.add_argument("--history", default=".pipewatch_history.json", metavar="FILE")
    p.add_argument("--baseline", default=".pipewatch_baseline.json", metavar="FILE")
    p.add_argument("--mute-file", default=".pipewatch_mute.json", metavar="FILE")
    p.add_argument("--window", type=int, default=10, metavar="N",
                   help="Number of recent runs to consider (default: 10)")
    p.add_argument("--pipeline", metavar="NAME",
                   help="Show health for a single pipeline only")
    p.add_argument("--json", dest="as_json", action="store_true",
                   help="Output as JSON")
    p.add_argument("--min-grade", metavar="GRADE", default=None,
                   help="Only show pipelines at or below this grade (e.g. C)")
    p.set_defaults(func=handle_health)


_GRADE_ORDER = ["A", "B", "C", "D", "F"]


def handle_health(args: argparse.Namespace) -> int:
    try:
        cfg = load_config(args.config)
        validate_config(cfg)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.pipeline:
        names = [args.pipeline]
    else:
        names = [p.name for p in cfg.pipelines]

    scores = all_health_scores(
        names,
        history_file=args.history,
        baseline_file=args.baseline,
        mute_file=args.mute_file,
        window=args.window,
    )

    if args.min_grade and args.min_grade.upper() in _GRADE_ORDER:
        cutoff = _GRADE_ORDER.index(args.min_grade.upper())
        scores = [s for s in scores if _GRADE_ORDER.index(s.grade) >= cutoff]

    if args.as_json:
        data = [
            {
                "pipeline": s.pipeline,
                "score": s.score,
                "grade": s.grade,
                "total_runs": s.total_runs,
                "recent_failures": s.recent_failures,
                "is_slow": s.is_slow,
                "is_muted": s.is_muted,
                "summary": s.summary,
            }
            for s in scores
        ]
        print(json.dumps(data, indent=2))
    else:
        print(format_health_text(scores))

    return 0
