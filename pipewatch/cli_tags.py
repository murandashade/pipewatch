"""CLI sub-commands for tag-based pipeline inspection."""
from __future__ import annotations
import argparse
import sys
from pipewatch.config import load_config, validate_config
from pipewatch.tags import all_tags, pipelines_matching_tags


def _add_subcommands(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("tags", help="Tag-based pipeline filtering")
    sub = p.add_subparsers(dest="tags_cmd", required=True)

    ls = sub.add_parser("list", help="List all tags defined in the config")
    ls.add_argument("--config", default="pipewatch.json")

    flt = sub.add_parser("filter", help="Show pipelines matching given tags")
    flt.add_argument("tags", nargs="+", metavar="TAG")
    flt.add_argument("--config", default="pipewatch.json")
    flt.add_argument(
        "--all",
        dest="match_all",
        action="store_true",
        help="Require all tags to match (AND semantics)",
    )

    p.set_defaults(func=handle_tags)


def handle_tags(args: argparse.Namespace) -> int:
    try:
        cfg = load_config(args.config)
        validate_config(cfg)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    pipelines = cfg.pipelines

    if args.tags_cmd == "list":
        tags = all_tags(pipelines)
        if not tags:
            print("No tags defined.")
        else:
            for t in tags:
                print(t)
        return 0

    if args.tags_cmd == "filter":
        matched = pipelines_matching_tags(pipelines, args.tags, match_all=args.match_all)
        if not matched:
            print("No pipelines match the given tags.")
            return 1
        for p in matched:
            print(p.name)
        return 0

    return 0
