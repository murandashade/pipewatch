"""Tests for pipewatch.cli_mute."""

from pathlib import Path
import argparse
import pytest

import pipewatch.mute as mute_mod
from pipewatch.cli_mute import handle_mute


class _Args:
    def __init__(self, action, pipeline, hours=1.0, state_file=None):
        self.mute_action = action
        self.pipeline = pipeline
        self.hours = hours
        self.state_file = str(state_file) if state_file else ".pipewatch/mute_state.json"


@pytest.fixture()
def sf(tmp_path):
    return tmp_path / "mute.json"


def test_mute_returns_zero(sf):
    args = _Args("mute", "pipe_a", hours=2.0, state_file=sf)
    assert handle_mute(args) == 0
    assert mute_mod.is_muted("pipe_a", path=sf)


def test_unmute_returns_zero(sf):
    mute_mod.mute_pipeline("pipe_a", hours=2, path=sf)
    args = _Args("unmute", "pipe_a", state_file=sf)
    assert handle_mute(args) == 0
    assert not mute_mod.is_muted("pipe_a", path=sf)


def test_unmute_not_muted_still_zero(sf, capsys):
    args = _Args("unmute", "pipe_a", state_file=sf)
    assert handle_mute(args) == 0
    captured = capsys.readouterr()
    assert "not muted" in captured.err.lower()


def test_check_not_muted_returns_zero(sf):
    args = _Args("check", "pipe_a", state_file=sf)
    assert handle_mute(args) == 0


def test_check_muted_returns_one(sf, capsys):
    mute_mod.mute_pipeline("pipe_a", hours=3, path=sf)
    args = _Args("check", "pipe_a", state_file=sf)
    assert handle_mute(args) == 1
    captured = capsys.readouterr()
    assert "MUTED" in captured.out
