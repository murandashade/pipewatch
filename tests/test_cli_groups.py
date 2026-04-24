"""Tests for pipewatch.cli_groups."""
from __future__ import annotations

import json
import pathlib

import pytest

from pipewatch.cli_groups import handle_groups


class _Args:
    def __init__(self, config: str, groups_cmd: str, group: str | None = None):
        self.config = config
        self.groups_cmd = groups_cmd
        self.group = group


@pytest.fixture()
def config_file(tmp_path: pathlib.Path):
    data = {
        "default_webhook": "https://hooks.example.com/test",
        "pipelines": [
            {"name": "ingest", "command": "echo ingest", "group": "etl"},
            {"name": "transform", "command": "echo transform", "group": "etl"},
            {"name": "report", "command": "echo report", "group": "reporting"},
        ],
    }
    p = tmp_path / "pipewatch.json"
    p.write_text(json.dumps(data))
    return str(p)


def test_list_returns_zero(config_file, capsys):
    rc = handle_groups(_Args(config_file, "list"))
    assert rc == 0
    out = capsys.readouterr().out
    assert "etl" in out
    assert "reporting" in out


def test_list_missing_config_returns_two(tmp_path):
    rc = handle_groups(_Args(str(tmp_path / "missing.json"), "list"))
    assert rc == 2


def test_show_returns_zero(config_file, capsys):
    rc = handle_groups(_Args(config_file, "show", group="etl"))
    assert rc == 0
    out = capsys.readouterr().out
    assert "ingest" in out
    assert "transform" in out


def test_show_unknown_group_returns_one(config_file, capsys):
    rc = handle_groups(_Args(config_file, "show", group="unknown"))
    assert rc == 1


def test_show_missing_config_returns_two(tmp_path):
    rc = handle_groups(_Args(str(tmp_path / "missing.json"), "show", group="etl"))
    assert rc == 2
