"""Tests for cli_schedule subcommands."""
from __future__ import annotations

import json
import types
from pathlib import Path

import pytest

from pipewatch.cli_schedule import handle_schedule


@pytest.fixture()
def config_file(tmp_path: Path):
    cfg = {
        "pipelines": [
            {"name": "alpha", "command": "echo hi", "schedule": "* * * * *"},
            {"name": "beta", "command": "echo bye"},
        ]
    }
    p = tmp_path / "pipewatch.json"
    p.write_text(json.dumps(cfg))
    return str(p)


def _args(**kwargs):
    base = types.SimpleNamespace(schedule_cmd="check", config="pipewatch.json")
    for k, v in kwargs.items():
        setattr(base, k, v)
    return base


def test_check_valid_cron(config_file, capsys):
    args = _args(schedule_cmd="check", config=config_file)
    rc = handle_schedule(args)
    assert rc == 0
    assert "valid" in capsys.readouterr().out


def test_check_invalid_cron(tmp_path, capsys):
    cfg = {"pipelines": [{"name": "bad", "command": "x", "schedule": "99 99 99"}]}
    p = tmp_path / "pipewatch.json"
    p.write_text(json.dumps(cfg))
    args = _args(schedule_cmd="check", config=str(p))
    rc = handle_schedule(args)
    assert rc == 1
    out = capsys.readouterr().out
    assert "bad" in out


def test_check_missing_config(capsys):
    args = _args(schedule_cmd="check", config="/no/such/file.json")
    rc = handle_schedule(args)
    assert rc == 2


def test_due_no_pipelines_due(config_file, capsys):
    # Use a specific time unlikely to match minute-only schedule issues
    args = _args(
        schedule_cmd="due",
        config=config_file,
        at="2024-01-15T03:00:00",
        as_json=False,
    )
    rc = handle_schedule(args)
    assert rc == 0


def test_due_json_output(config_file, capsys):
    args = _args(
        schedule_cmd="due",
        config=config_file,
        at="2024-06-01T12:30:00",
        as_json=True,
    )
    rc = handle_schedule(args)
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "due" in data
    assert "at" in data
    assert "alpha" in data["due"]  # * * * * * always matches


def test_due_invalid_at(config_file, capsys):
    args = _args(
        schedule_cmd="due",
        config=config_file,
        at="not-a-date",
        as_json=False,
    )
    rc = handle_schedule(args)
    assert rc == 2
