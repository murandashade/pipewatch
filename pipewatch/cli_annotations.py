"""CLI subcommands for pipeline annotations."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pipewatch.annotations import (
    add_annotation,
    get_annotations,
    delete_annotations,
    format_annotations_text,
)

_DEFAULT_FILE = ".pipewatch/annotations.json"


def _add_subcommands(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("annotate", help="Manage pipeline annotations")
    p.add_argument("--file", default=_DEFAULT_FILE)
    s = p.add_subparsers(dest="ann_cmd", required=True)

    add_p = s.add_parser("add", help="Add an annotation")
    add_p.add_argument("pipeline")
    add_p.add_argument("note")
    add_p.add_argument("--author", default="")

    show_p = s.add_parser("show", help="Show annotations")
    show_p.add_argument("pipeline")

    del_p = s.add_parser("delete", help="Delete all annotations for a pipeline")
    del_p.add_argument("pipeline")

    p.set_defaults(func=handle_annotations)


def handle_annotations(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if args.ann_cmd == "add":
        entry = add_annotation(path, args.pipeline, args.note, args.author)
        print(f"Annotation added at {entry['timestamp']}")
        return 0
    if args.ann_cmd == "show":
        notes = get_annotations(path, args.pipeline)
        print(format_annotations_text(notes))
        return 0
    if args.ann_cmd == "delete":
        count = delete_annotations(path, args.pipeline)
        print(f"Deleted {count} annotation(s) for '{args.pipeline}'.")
        return 0
    print(f"Unknown subcommand: {args.ann_cmd}", file=sys.stderr)
    return 2
