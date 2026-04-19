"""CLI subcommands for pipeline output snapshots."""
from __future__ import annotations

import argparse
import sys

from pipewatch import snapshots

_DEFAULT_DIR = ".pipewatch/snapshots"


def _add_subcommands(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("snapshot", help="Manage pipeline output snapshots")
    ss = p.add_subparsers(dest="snapshot_cmd", required=True)

    show = ss.add_parser("show", help="Show stored snapshot for a pipeline")
    show.add_argument("name", help="Pipeline name")
    show.add_argument("--snapshot-dir", default=_DEFAULT_DIR)

    diff = ss.add_parser("diff", help="Check if output differs from snapshot")
    diff.add_argument("name", help="Pipeline name")
    diff.add_argument("output", help="Current output string to compare")
    diff.add_argument("--snapshot-dir", default=_DEFAULT_DIR)

    save = ss.add_parser("save", help="Save a snapshot for a pipeline")
    save.add_argument("name", help="Pipeline name")
    save.add_argument("output", help="Output string to snapshot")
    save.add_argument("--snapshot-dir", default=_DEFAULT_DIR)

    p.set_defaults(func=handle_snapshot)


def handle_snapshot(args: argparse.Namespace) -> int:
    cmd = args.snapshot_cmd
    d = args.snapshot_dir

    if cmd == "show":
        snap = snapshots.load_snapshot(args.name, base_dir=d)
        if snap is None:
            print(f"No snapshot found for '{args.name}'.", file=sys.stderr)
            return 1
        print(f"Pipeline : {snap['name']}")
        print(f"Timestamp: {snap['timestamp']}")
        print(f"Checksum : {snap['checksum']}")
        print(f"Output   : {snap['output']}")
        return 0

    if cmd == "diff":
        summary = snapshots.diff_summary(args.name, args.output, base_dir=d)
        print(summary)
        changed = snapshots.has_changed(args.name, args.output, base_dir=d)
        return 1 if changed else 0

    if cmd == "save":
        rec = snapshots.save_snapshot(args.name, args.output, base_dir=d)
        print(f"Snapshot saved for '{rec['name']}' at {rec['timestamp']}.")
        return 0

    return 2
