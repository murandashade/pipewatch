"""Subcommands for schedule inspection."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from pipewatch.scheduler import due_pipelines, parse_cron
from pipewatch.config import load_config, validate_config


def _add_subcommands(sub: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = sub.add_parser("schedule", help="Inspect pipeline schedules")
    s = p.add_subparsers(dest="schedule_cmd", required=True)

    chk = s.add_parser("check", help="Validate cron expressions in config")
    chk.add_argument("--config", default="pipewatch.json")

    due = s.add_parser("due", help="List pipelines due at a given time")
    due.add_argument("--config", default="pipewatch.json")
    due.add_argument("--at", default=None, help="ISO datetime (default: now)")
    due.add_argument("--json", dest="as_json", action="store_true")

    p.set_defaults(func=handle_schedule)


def handle_schedule(args: argparse.Namespace) -> int:
    if args.schedule_cmd == "check":
        return _handle_check(args)
    if args.schedule_cmd == "due":
        return _handle_due(args)
    return 1


def _handle_check(args: argparse.Namespace) -> int:
    try:
        cfg = load_config(args.config)
        validate_config(cfg)
    except Exception as exc:  # noqa: BLE001
        print(f"Config error: {exc}")
        return 2

    errors = []
    for pl in cfg.pipelines:
        if pl.schedule is None:
            continue
        try:
            parse_cron(pl.schedule)
        except ValueError as exc:
            errors.append(f"  {pl.name}: {exc}")

    if errors:
        print("Invalid cron expressions:")
        print("\n".join(errors))
        return 1

    print("All cron expressions are valid.")
    return 0


def _handle_due(args: argparse.Namespace) -> int:
    try:
        cfg = load_config(args.config)
        validate_config(cfg)
    except Exception as exc:  # noqa: BLE001
        print(f"Config error: {exc}")
        return 2

    if args.at:
        try:
            at = datetime.fromisoformat(args.at).replace(tzinfo=timezone.utc)
        except ValueError:
            print(f"Invalid --at value: {args.at}")
            return 2
    else:
        at = datetime.now(timezone.utc)

    names = [pl.name for pl in due_pipelines(cfg.pipelines, at)]

    if args.as_json:
        print(json.dumps({"due": names, "at": at.isoformat()}))
    else:
        if names:
            print(f"Pipelines due at {at.isoformat()}:")
            for n in names:
                print(f"  - {n}")
        else:
            print(f"No pipelines due at {at.isoformat()}.")
    return 0
