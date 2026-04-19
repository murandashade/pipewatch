"""Integration-level tests: baseline subcommand is wired into the CLI parser."""

import argparse
from pipewatch.cli_baseline import _add_subcommands


def _make_parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    _add_subcommands(sub)
    return p


def test_subcommand_registered():
    p = _make_parser()
    args = p.parse_args(["baseline", "show", "my_pipe"])
    assert args.baseline_cmd == "show"
    assert args.pipeline == "my_pipe"


def test_record_subcommand_args():
    p = _make_parser()
    args = p.parse_args(["baseline", "record", "etl", "4.2"])
    assert args.baseline_cmd == "record"
    assert args.duration == pytest.approx(4.2)


def test_check_default_threshold():
    p = _make_parser()
    args = p.parse_args(["baseline", "check", "etl", "5.0"])
    assert args.threshold == 2.0


def test_custom_baseline_file():
    p = _make_parser()
    args = p.parse_args(["baseline", "show", "etl", "--baseline-file", "/tmp/b.json"])
    assert args.baseline_file == "/tmp/b.json"


import pytest
