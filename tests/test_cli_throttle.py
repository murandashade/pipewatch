"""Tests for pipewatch.cli_throttle."""
from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from pipewatch.cli_throttle import _add_subcommands, handle_throttle


class _Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def test_check_not_throttled(tmp_path, capsys):
    args = _Args(throttle_cmd="check", pipeline="p1", window=300, state_dir=str(tmp_path))
    rc = handle_throttle(args)
    assert rc == 0
    assert "not throttled" in capsys.readouterr().out


def test_check_throttled(tmp_path, capsys):
    from pipewatch.throttle import record_alert
    record_alert("p1", state_dir=str(tmp_path))
    args = _Args(throttle_cmd="check", pipeline="p1", window=300, state_dir=str(tmp_path))
    rc = handle_throttle(args)
    assert rc == 0
    assert "throttled" in capsys.readouterr().out


def test_record_creates_state(tmp_path, capsys):
    args = _Args(throttle_cmd="record", pipeline="p2", state_dir=str(tmp_path))
    rc = handle_throttle(args)
    assert rc == 0
    from pipewatch.throttle import is_throttled
    assert is_throttled("p2", 300, state_dir=str(tmp_path)) is True


def test_clear_removes_state(tmp_path, capsys):
    from pipewatch.throttle import record_alert, is_throttled
    record_alert("p3", state_dir=str(tmp_path))
    args = _Args(throttle_cmd="clear", pipeline="p3", state_dir=str(tmp_path))
    rc = handle_throttle(args)
    assert rc == 0
    assert is_throttled("p3", 300, state_dir=str(tmp_path)) is False


def test_unknown_cmd_returns_two(tmp_path, capsys):
    args = _Args(throttle_cmd="bogus", pipeline="p", state_dir=str(tmp_path))
    rc = handle_throttle(args)
    assert rc == 2


def test_subcommand_registered():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    _add_subcommands(sub)
    ns = parser.parse_args(["throttle", "check", "my_pipe", "--window", "60"])
    assert ns.pipeline == "my_pipe"
    assert ns.window == 60
