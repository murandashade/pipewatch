"""Tests for the history CLI subcommands."""

import json
import pytest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from pipewatch.cli_history import handle_history


@pytest.fixture
def hist_file(tmp_path):
    return tmp_path / "history.json"


def _entry(pipeline, status, ts="2024-01-15T10:00:00", duration=1.0, message=""):
    return {
        "pipeline": pipeline,
        "status": status,
        "timestamp": ts,
        "duration": duration,
        "message": message,
    }


def _write(path, entries):
    path.write_text(json.dumps(entries))


def _args(hist_file, pipeline=None, last=None, failures_only=False):
    return SimpleNamespace(
        history_file=str(hist_file),
        pipeline=pipeline,
        last=last,
        failures_only=failures_only,
    )


def test_handle_history_empty_file(hist_file, capsys):
    hist_file.write_text("[]")
    args = _args(hist_file)
    rc = handle_history(args)
    out = capsys.readouterr().out
    assert rc == 0
    assert "No history" in out or out.strip() == "" or "0" in out


def test_handle_history_missing_file(hist_file, capsys):
    args = _args(hist_file)  # file does not exist
    rc = handle_history(args)
    out = capsys.readouterr().out
    assert rc == 0


def test_handle_history_shows_entries(hist_file, capsys):
    entries = [
        _entry("etl_load", "success", ts="2024-01-15T09:00:00"),
        _entry("etl_load", "failure", ts="2024-01-15T10:00:00", message="timeout"),
    ]
    _write(hist_file, entries)
    args = _args(hist_file)
    rc = handle_history(args)
    out = capsys.readouterr().out
    assert rc == 0
    assert "etl_load" in out


def test_handle_history_filter_by_pipeline(hist_file, capsys):
    entries = [
        _entry("etl_load", "success"),
        _entry("etl_transform", "failure"),
    ]
    _write(hist_file, entries)
    args = _args(hist_file, pipeline="etl_load")
    rc = handle_history(args)
    out = capsys.readouterr().out
    assert rc == 0
    assert "etl_load" in out
    assert "etl_transform" not in out


def test_handle_history_failures_only(hist_file, capsys):
    entries = [
        _entry("etl_load", "success"),
        _entry("etl_load", "failure", message="disk full"),
    ]
    _write(hist_file, entries)
    args = _args(hist_file, failures_only=True)
    rc = handle_history(args)
    out = capsys.readouterr().out
    assert rc == 0
    assert "failure" in out or "disk full" in out


def test_handle_history_last_limits_output(hist_file, capsys):
    entries = [_entry("pipe", "success", ts=f"2024-01-{i+1:02d}T00:00:00") for i in range(10)]
    _write(hist_file, entries)
    args = _args(hist_file, last=3)
    rc = handle_history(args)
    out = capsys.readouterr().out
    assert rc == 0
    # Only 3 entries should appear — count pipeline name occurrences
    assert out.count("pipe") <= 3
