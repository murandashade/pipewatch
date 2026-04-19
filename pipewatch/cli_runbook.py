"""CLI subcommands for managing pipeline runbooks."""
from __future__ import annotations

import argparse
import sys

from pipewatch import runbook as rb

_DEFAULT_FILE = rb._DEFAULT_FILE


def _add_subcommands(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("runbook", help="Manage pipeline runbooks")
    s = p.add_subparsers(dest="runbook_cmd", required=True)

    add = s.add_parser("add", help="Add a runbook link")
    add.add_argument("pipeline")
    add.add_argument("url")
    add.add_argument("--note", default="")
    add.add_argument("--file", default=_DEFAULT_FILE)

    show = s.add_parser("show", help="Show runbooks for a pipeline")
    show.add_argument("pipeline")
    show.add_argument("--file", default=_DEFAULT_FILE)

    rm = s.add_parser("remove", help="Remove a runbook link")
    rm.add_argument("pipeline")
    rm.add_argument("url")
    rm.add_argument("--file", default=_DEFAULT_FILE)

    ls = s.add_parser("list", help="List all runbooks")
    ls.add_argument("--file", default=_DEFAULT_FILE)


def handle_runbook(args: argparse.Namespace) -> int:
    cmd = args.runbook_cmd
    if cmd == "add":
        entry = rb.add_runbook(args.pipeline, args.url, note=args.note, path=args.file)
        print(f"Added: {entry['url']}")
        return 0
    if cmd == "show":
        entries = rb.get_runbooks(args.pipeline, path=args.file)
        print(rb.format_runbooks_text(args.pipeline, entries))
        return 0
    if cmd == "remove":
        ok = rb.remove_runbook(args.pipeline, args.url, path=args.file)
        if not ok:
            print(f"No runbook with url '{args.url}' found.", file=sys.stderr)
            return 1
        print("Removed.")
        return 0
    if cmd == "list":
        data = rb.all_runbooks(path=args.file)
        if not data:
            print("No runbooks recorded.")
            return 0
        for pipeline, entries in data.items():
            print(rb.format_runbooks_text(pipeline, entries))
        return 0
    return 1
