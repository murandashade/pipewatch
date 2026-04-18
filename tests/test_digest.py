"""Tests for pipewatch.digest."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from pipewatch.digest import build_digest, format_digest_text


@pytest.fixture()
def hist_file(tmp_path: Path) -> Path:
    return tmp_path / "history.jsonl"


def _write(path: Path, records: list[dict]) -> None:
    with path.open("w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


NOW = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)


def test_build_digest_empty_file(hist_file: Path) -> None:
    hist_file.write_text("")
    digest = build_digest(hist_file)
    assert digest["total_runs"] == 0
    assert digest["failed_runs"] == 0
    assert digest["pipelines"] == {}


def test_build_digest_counts(hist_file: Path) -> None:
    _write(hist_file, [
        {"pipeline": "etl", "success": True, "timestamp": NOW.isoformat()},
        {"pipeline": "etl", "success": False, "timestamp": NOW.isoformat()},
        {"pipeline": "sync", "success": True, "timestamp": NOW.isoformat()},
    ])
    digest = build_digest(hist_file)
    assert digest["total_runs"] == 3
    assert digest["successful_runs"] == 2
    assert digest["failed_runs"] == 1
    assert digest["pipelines"]["etl"] == {"total": 2, "failures": 1}
    assert digest["pipelines"]["sync"] == {"total": 1, "failures": 0}


def test_build_digest_since_filters(hist_file: Path) -> None:
    old = (NOW - timedelta(days=2)).isoformat()
    _write(hist_file, [
        {"pipeline": "etl", "success": False, "timestamp": old},
        {"pipeline": "etl", "success": True, "timestamp": NOW.isoformat()},
    ])
    digest = build_digest(hist_file, since=NOW)
    assert digest["total_runs"] == 1
    assert digest["failed_runs"] == 0


def test_build_digest_missing_file(hist_file: Path) -> None:
    digest = build_digest(hist_file)
    assert digest["total_runs"] == 0


def test_format_digest_text_contains_summary(hist_file: Path) -> None:
    _write(hist_file, [
        {"pipeline": "etl", "success": False, "timestamp": NOW.isoformat()},
    ])
    digest = build_digest(hist_file)
    text = format_digest_text(digest)
    assert "pipewatch digest" in text
    assert "1 failed" in text
    assert "etl" in text


def test_format_digest_since_all_time(hist_file: Path) -> None:
    hist_file.write_text("")
    digest = build_digest(hist_file)
    text = format_digest_text(digest)
    assert "all time" in text
