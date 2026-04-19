"""CLI subcommands for muting/unmuting pipeline alerts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pipewatch import mute as mute_mod

_DEFAULT_STATE = Path(".pipewatch") / "mute_state.json"


def _add_subcommands(sub: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p_mute = sub.add_parser("mute", help="Mute alerts for a pipeline")
    p_mute.add_argument("pipeline", help="Pipeline name")
    p_mute.add_argument("--hours", type=float, default=1.0,
                        help="Duration to mute in hours (default: 1)")
    p_mute.add_argument("--state-file", default=str(_DEFAULT_STATE))
    p_mute.set_defaults(mute_action="mute")

    p_unmute = sub.add_parser("unmute", help="Unmute alerts for a pipeline")
    p_unmute.add_argument("pipeline", help="Pipeline name")
    p_unmute.add_argument("--state-file", default=str(_DEFAULT_STATE))
    p_unmute.set_defaults(mute_action="unmute")

    p_check = sub.add_parser("mute-check", help="Check if a pipeline is muted")
    p_check.add_argument("pipeline", help="Pipeline name")
    p_check.add_argument("--state-file", default=str(_DEFAULT_STATE))
    p_check.set_defaults(mute_action="check")


def handle_mute(args: argparse.Namespace) -> int:
    path = Path(args.state_file)
    action = args.mute_action

    if action == "mute":
        mute_mod.mute_pipeline(args.pipeline, hours=args.hours, path=path)
        print(f"Muted '{args.pipeline}' for {args.hours} hour(s).")
        return 0

    if action == "unmute":
        removed = mute_mod.unmute_pipeline(args.pipeline, path=path)
        if removed:
            print(f"Unmuted '{args.pipeline}'.")
        else:
            print(f"'{args.pipeline}' was not muted.", file=sys.stderr)
        return 0

    if action == "check":
        if mute_mod.is_muted(args.pipeline, path=path):
            until = mute_mod.muted_until(args.pipeline, path=path)
            print(f"MUTED until {until}")
            return 1
        print("NOT MUTED")
        return 0

    print("Unknown action.", file=sys.stderr)
    return 2
