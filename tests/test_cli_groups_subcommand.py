"""Parser-level tests for the 'groups' sub-command."""
from __future__ import annotations

import argparse

from pipewatch.cli_groups import _add_subcommands


def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    _add_subcommands(sub)
    return parser


def test_subcommand_registered():
    parser = _make_parser()
    args = parser.parse_args(["groups", "list"])
    assert args.command == "groups"


def test_list_default_config():
    parser = _make_parser()
    args = parser.parse_args(["groups", "list"])
    assert args.config == "pipewatch.json"


def test_list_custom_config():
    parser = _make_parser()
    args = parser.parse_args(["groups", "list", "--config", "custom.json"])
    assert args.config == "custom.json"


def test_show_captures_group():
    parser = _make_parser()
    args = parser.parse_args(["groups", "show", "etl"])
    assert args.group == "etl"
    assert args.groups_cmd == "show"


def test_show_default_config():
    parser = _make_parser()
    args = parser.parse_args(["groups", "show", "etl"])
    assert args.config == "pipewatch.json"
