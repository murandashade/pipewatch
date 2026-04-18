"""Tests for pipewatch.cli_retention."""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from pipewatch.cli_retention import handle_prune


def _entry(days_ago: float) -> str:
    ts = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
    return json.dumps({"pipeline": "p", "success": True, "timestamp": ts})


class _Args:
    def __init__(self, history_dir, pipeline=None, max_age_days=None, max_entries=None):
        self.history_dir = str(history_dir)
        self.pipeline = pipeline
        self.max_age_days = max_age_days
        self.max_entries = max_entries


def test_no_criteria_returns_error(tmp_path: Path, capsys) -> None:
    rc = handle_prune(_Args(tmp_path))
    assert rc == 2
    assert "required" in capsys.readouterr().out


def test_prune_single_pipeline(tmp_path: Path, capsys) -> None:
    f = tmp_path / "mypipe.jsonl"
    f.write_text(_entry(10) + "\n" + _entry(1) + "\n")
    rc = handle_prune(_Args(tmp_path, pipeline="mypipe", max_age_days=7))
    assert rc == 0
    out = capsys.readouterr().out
    assert "1" in out
    assert "mypipe" in out


def test_prune_all_pipelines(tmp_path: Path, capsys) -> None:
    for name in ("alpha", "beta"):
        (tmp_path / f"{name}.jsonl").write_text(
            _entry(20) + "\n" + _entry(2) + "\n"
        )
    rc = handle_prune(_Args(tmp_path, max_age_days=7))
    assert rc == 0
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out
    assert "Total pruned: 2" in out


def test_prune_missing_dir_no_crash(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "no_such_dir"
    rc = handle_prune(_Args(missing, max_entries=5))
    assert rc == 0
    assert "Total pruned: 0" in capsys.readouterr().out
