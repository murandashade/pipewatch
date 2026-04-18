"""CLI sub-commands for schedule inspection."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

from pipewatch.scheduler import is_due, due_pipelines


def _add_subcommands(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    sp = subparsers.add_parser(
        'schedule',
        help='Inspect pipeline schedules',
    )
    sub = sp.add_subparsers(dest='schedule_cmd', required=True)

    check = sub.add_parser('check', help='Check if a cron expression is due now')
    check.add_argument('expr', help="Cron expression e.g. '30 14 * * *'")

    sub.add_parser('due', help='List pipelines due to run now')

    sp.set_defaults(func=handle_schedule)


def handle_schedule(args: argparse.Namespace, config=None) -> int:
    if args.schedule_cmd == 'check':
        return _handle_check(args)
    if args.schedule_cmd == 'due':
        return _handle_due(args, config)
    return 1


def _handle_check(args: argparse.Namespace) -> int:
    try:
        now = datetime.now(tz=timezone.utc)
        result = is_due(args.expr, at=now)
        status = 'DUE' if result else 'NOT DUE'
        print(f"{args.expr!r} is {status} at {now.strftime('%Y-%m-%dT%H:%M')} UTC")
        return 0 if result else 1
    except ValueError as exc:
        print(f"Error: {exc}")
        return 2


def _handle_due(args: argparse.Namespace, config) -> int:
    if config is None:
        print('No config loaded.')
        return 1
    now = datetime.now(tz=timezone.utc)
    pipelines = due_pipelines(config, at=now)
    if not pipelines:
        print('No pipelines are due right now.')
        return 0
    print(f"{len(pipelines)} pipeline(s) due at {now.strftime('%Y-%m-%dT%H:%M')} UTC:")
    for p in pipelines:
        print(f"  - {p.name}  [{p.schedule}]")
    return 0
