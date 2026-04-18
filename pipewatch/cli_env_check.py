"""CLI subcommand: pipewatch env-check."""
from __future__ import annotations

import argparse
import json
import sys

from pipewatch.config import load_config, validate_config
from pipewatch.env_check import check_all_envs, format_env_check_text


def _add_subcommands(subparsers) -> None:
    p = subparsers.add_parser("env-check", help="Validate required environment variables")
    p.add_argument("--config", default="pipewatch.json", help="Config file path")
    p.add_argument("--json", dest="as_json", action="store_true", help="Output as JSON")
    p.set_defaults(func=handle_env_check)


def handle_env_check(args: argparse.Namespace) -> int:
    try:
        cfg = load_config(args.config)
        validate_config(cfg)
    except FileNotFoundError:
        print(f"Config not found: {args.config}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"Invalid config: {exc}", file=sys.stderr)
        return 2

    results = check_all_envs(cfg.pipelines)

    if args.as_json:
        data = [
            {
                "pipeline": r.pipeline,
                "ok": r.ok,
                "present": r.present,
                "missing": r.missing,
            }
            for r in results
        ]
        print(json.dumps(data, indent=2))
    else:
        print(format_env_check_text(results))

    any_failed = any(not r.ok for r in results)
    return 1 if any_failed else 0
