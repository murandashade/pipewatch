"""Tests for pipewatch.retention."""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from pipewatch.retention import prune_history, prune_all


@pytest.fixture()
def hist_file(tmp_path: Path) -> Path:
    return tmp_path / "pipeline_a.jsonl"


def _entry(days_ago: float, pipeline: str = "a", success: bool = True) -> str:
    ts = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
    return json.dumps({"pipeline": pipeline, "success": success, "timestamp": ts})


def test_prune_missing_file_returns_zero(hist_file: Path) -> None:
    assert prune_history(hist_file, max_age_days=7) == 0


def test_prune_by_age_removes_old_entries(hist_file: Path) -> None:
    hist_file.write_text(
        _entry(10) + "\n" + _entry(3) + "\n" + _entry(1) + "\n"
    )
    removed = prune_history(hist_file, max_age_days=7)
    assert removed == 1
    remaining = [json.loads(l) for l in hist_file.read_text().splitlines() if l]
    assert len(remaining) == 2


def test_prune_by_max_entries_keeps_newest(hist_file: Path) -> None:
    hist_file.write_text(
        _entry(5) + "\n" + _entry(3) + "\n" + _entry(1) + "\n"
    )
    removed = prune_history(hist_file, max_entries=2)
    assert removed == 1
    remaining = [json.loads(l) for l in hist_file.read_text().splitlines() if l]
    assert len(remaining) == 2


def test_prune_combined_age_and_entries(hist_file: Path) -> None:
    hist_file.write_text(
        _entry(20) + "\n" + _entry(10) + "\n" + _entry(3) + "\n" + _entry(1) + "\n"
    )
    removed = prune_history(hist_file, max_age_days=14, max_entries=1)
    assert removed == 3


def test_prune_no_criteria_removes_nothing(hist_file: Path) -> None:
    hist_file.write_text(_entry(100) + "\n" + _entry(200) + "\n")
    removed = prune_history(hist_file)
    assert removed == 0


def test_prune_all_covers_multiple_files(tmp_path: Path) -> None:
    for name in ("pipe_a", "pipe_b"):
        f = tmp_path / f"{name}.jsonl"
        f.write_text(_entry(10) + "\n" + _entry(1) + "\n")
    results = prune_all(tmp_path, max_age_days=7)
    assert results == {"pipe_a": 1, "pipe_b": 1}


def test_prune_all_empty_dir(tmp_path: Path) -> None:
    assert prune_all(tmp_path, max_age_days=7) == {}
