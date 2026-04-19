"""CLI subcommands for pipeline label inspection and filtering."""
from __future__ import annotations
import argparse
import sys
from pipewatch.config import load_config, validate_config
from pipewatch.labels import (
    pipelines_matching_labels,
    all_label_keys,
    format_labels_text,
)


def _add_subcommands(sub: argparse.Action) -> None:
    p = sub.add_parser("labels", help="inspect and filter pipeline labels")
    p.add_argument("--config", default="pipewatch.json")
    p.add_argument("--filter", metavar="KEY=VALUE", nargs="+", dest="filters",
                   help="filter pipelines by label (all must match)")
    p.add_argument("--any", action="store_true", dest="match_any",
                   help="match pipelines with ANY of the given labels")
    p.add_argument("--keys", action="store_true", help="list all label keys instead")
    p.set_defaults(func=handle_labels)


def _parse_filters(filters: list[str]) -> dict[str, str]:
    result = {}
    for f in filters or []:
        if "=" not in f:
            raise ValueError(f"Invalid label filter: {f!r} (expected KEY=VALUE)")
        k, v = f.split("=", 1)
        result[k.strip()] = v.strip()
    return result


def handle_labels(args: argparse.Namespace) -> int:
    try:
        cfg = load_config(args.config)
        validate_config(cfg)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    pipelines = cfg.pipelines

    if args.keys:
        keys = all_label_keys(pipelines)
        if keys:
            print("\n".join(keys))
        else:
            print("No label keys defined.")
        return 0

    if args.filters:
        try:
            label_map = _parse_filters(args.filters)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        pipelines = pipelines_matching_labels(pipelines, label_map, match_all=not args.match_any)

    print(format_labels_text(pipelines))
    return 0
