"""CLI sub-commands for pipeline groups."""
from __future__ import annotations

import argparse
import sys
from typing import List

from pipewatch.cli import _load_and_validate
from pipewatch.pipeline_groups import all_groups, format_groups_text, group_map, pipelines_in_group


def _add_subcommands(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("groups", help="Manage and inspect pipeline groups")
    gsub = p.add_subparsers(dest="groups_cmd", required=True)

    ls = gsub.add_parser("list", help="List all groups")
    ls.add_argument("--config", default="pipewatch.json")

    show = gsub.add_parser("show", help="Show pipelines in a group")
    show.add_argument("group", help="Group name")
    show.add_argument("--config", default="pipewatch.json")


def handle_groups(args: argparse.Namespace) -> int:
    cfg, err = _load_and_validate(args.config)
    if err:
        print(err, file=sys.stderr)
        return 2

    pipelines = cfg.pipelines  # type: ignore[union-attr]

    if args.groups_cmd == "list":
        groups = all_groups(pipelines)
        if not groups:
            print("No groups defined.")
        else:
            for g in groups:
                print(g)
        return 0

    if args.groups_cmd == "show":
        members = pipelines_in_group(pipelines, args.group)
        if not members:
            print(f"No pipelines found in group '{args.group}'.")
            return 1
        for p in members:
            print(p.name)
        return 0

    return 0
