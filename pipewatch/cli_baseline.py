"""CLI subcommands for baseline duration management."""

from __future__ import annotations

import argparse
import sys

from pipewatch.baseline import (
    get_baseline,
    format_baseline_text,
    record_duration,
    DEFAULT_BASELINE_FILE,
)


def _add_subcommands(sub: argparse.Action) -> None:
    p = sub.add_parser("baseline", help="manage pipeline duration baselines")
    s = p.add_subparsers(dest="baseline_cmd", required=True)

    show = s.add_parser("show", help="show baseline stats for a pipeline")
    show.add_argument("pipeline", help="pipeline name")
    show.add_argument("--baseline-file", default=DEFAULT_BASELINE_FILE)

    rec = s.add_parser("record", help="record a duration sample")
    rec.add_argument("pipeline", help="pipeline name")
    rec.add_argument("duration", type=float, help="duration in seconds")
    rec.add_argument("--baseline-file", default=DEFAULT_BASELINE_FILE)

    chk = s.add_parser("check", help="check if a duration is slow")
    chk.add_argument("pipeline")
    chk.add_argument("duration", type=float)
    chk.add_argument("--threshold", type=float, default=2.0)
    chk.add_argument("--baseline-file", default=DEFAULT_BASELINE_FILE)

    p.set_defaults(func=handle_baseline)


def handle_baseline(args: argparse.Namespace) -> int:
    if args.baseline_cmd == "show":
        print(format_baseline_text(args.pipeline, args.baseline_file))
        return 0

    if args.baseline_cmd == "record":
        record_duration(args.pipeline, args.duration, args.baseline_file)
        print(f"Recorded {args.duration}s for '{args.pipeline}'.")
        return 0

    if args.baseline_cmd == "check":
        from pipewatch.baseline import is_slow
        baseline = get_baseline(args.pipeline, args.baseline_file)
        if baseline is None:
            print(f"No baseline for '{args.pipeline}'.")
            return 1
        slow = is_slow(args.pipeline, args.duration, args.threshold, args.baseline_file)
        status = "SLOW" if slow else "OK"
        print(f"{args.pipeline}: {args.duration}s vs baseline {baseline}s — {status}")
        return 2 if slow else 0

    return 1
