"""CLI subcommand: pipewatch deps — show pipeline execution order."""
from __future__ import annotations
import argparse
import json
import sys
from pipewatch.config import load_config, validate_config
from pipewatch.dependency import execution_order, CycleError


def _add_subcommands(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("deps", help="Show pipeline dependency execution order")
    p.add_argument("--config", default="pipewatch.json", help="Config file path")
    p.add_argument("--json", dest="as_json", action="store_true", help="Output as JSON")
    p.set_defaults(func=handle_deps)


def handle_deps(args: argparse.Namespace) -> int:
    try:
        cfg = load_config(args.config)
        validate_config(cfg)
    except FileNotFoundError:
        print(f"Config file not found: {args.config}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"Config error: {exc}", file=sys.stderr)
        return 2

    try:
        ordered = execution_order(cfg.pipelines)
    except CycleError as exc:
        print(f"Dependency cycle: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Dependency error: {exc}", file=sys.stderr)
        return 1

    if args.as_json:
        out = [
            {"name": p.name, "depends_on": getattr(p, "depends_on", None) or []}
            for p in ordered
        ]
        print(json.dumps(out, indent=2))
    else:
        print("Execution order:")
        for i, p in enumerate(ordered, 1):
            deps = getattr(p, "depends_on", None) or []
            dep_str = f"  (depends on: {', '.join(deps)})" if deps else ""
            print(f"  {i}. {p.name}{dep_str}")

    return 0
