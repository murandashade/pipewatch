"""Tests that the health subcommand is correctly wired into argparse."""

from __future__ import annotations

import argparse

from pipewatch.cli_health import _add_subcommands


def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    _add_subcommands(sub)
    return parser


def test_subcommand_registered():
    parser = _make_parser()
    args = parser.parse_args(["health", "--config", "my.json"])
    assert args.command == "health"
    assert args.config == "my.json"


def test_default_window_is_ten():
    parser = _make_parser()
    args = parser.parse_args(["health"])
    assert args.window == 10


def test_json_flag_default_false():
    parser = _make_parser()
    args = parser.parse_args(["health"])
    assert args.as_json is False


def test_json_flag_true():
    parser = _make_parser()
    args = parser.parse_args(["health", "--json"])
    assert args.as_json is True


def test_pipeline_filter_captured():
    parser = _make_parser()
    args = parser.parse_args(["health", "--pipeline", "my_pipe"])
    assert args.pipeline == "my_pipe"


def test_min_grade_captured():
    parser = _make_parser()
    args = parser.parse_args(["health", "--min-grade", "C"])
    assert args.min_grade == "C"


def test_custom_history_file():
    parser = _make_parser()
    args = parser.parse_args(["health", "--history", "custom.json"])
    assert args.history == "custom.json"
