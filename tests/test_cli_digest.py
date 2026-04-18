"""Tests for pipewatch.cli_digest."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from pipewatch.cli_digest import _add_subcommands, handle_digest


@pytest.fixture()
def hist_file(tmp_path: Path) -> Path:
    return tmp_path / "history.jsonl"


def _write(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n")


def _args(hist_file: Path, since_hours: float = 24.0, as_json: bool = False) -> argparse.Namespace:
    return argparse.Namespace(
        history_file=str(hist_file),
        since_hours=since_hours,
        json=as_json,
    )


def test_missing_history_file_returns_two(tmp_path: Path, capsys):
    ns = _args(tmp_path / "missing.jsonl")
    rc = handle_digest(ns)
    assert rc == 2
    captured = capsys.readouterr()
    assert "not found" in captured.err


def test_returns_zero_on_success(hist_file: Path, capsys):
    _write(hist_file, [
        '{"pipeline": "etl", "success": true, "timestamp": "2099-01-01T00:00:00+00:00"}',
    ])
    ns = _args(hist_file)
    rc = handle_digest(ns)
    assert rc == 0


def test_text_output_contains_totals(hist_file: Path, capsys):
    _write(hist_file, [
        '{"pipeline": "etl", "success": true, "timestamp": "2099-01-01T00:00:00+00:00"}',
        '{"pipeline": "etl", "success": false, "timestamp": "2099-01-01T01:00:00+00:00"}',
    ])
    ns = _args(hist_file)
    handle_digest(ns)
    out = capsys.readouterr().out
    assert "2" in out  # total runs


def test_json_output_is_valid(hist_file: Path, capsys):
    _write(hist_file, [
        '{"pipeline": "etl", "success": true, "timestamp": "2099-01-01T00:00:00+00:00"}',
    ])
    ns = _args(hist_file, as_json=True)
    rc = handle_digest(ns)
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "total" in data
    assert "by_pipeline" in data


def test_subcommand_registered():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    _add_subcommands(sub)
    ns = parser.parse_args(["digest", "--json"])
    assert ns.json is True
    assert ns.since_hours == 24.0
