"""Tests for pipewatch.pipeline_compare."""
from __future__ import annotations

import json
import pathlib
from datetime import datetime, timezone

import pytest

from pipewatch.pipeline_compare import (
    compare_pipeline,
    format_compare_text,
    CompareResult,
)


@pytest.fixture()
def hist_file(tmp_path: pathlib.Path) -> pathlib.Path:
    return tmp_path / "history.jsonl"


def _entry(name: str, success: bool, ts: str, duration: float = 1.0) -> str:
    return json.dumps(
        {"pipeline": name, "success": success, "timestamp": ts, "duration_seconds": duration}
    )


def _write(path: pathlib.Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n")


# ── helpers ──────────────────────────────────────────────────────────────────

WINDOW_A_START = datetime(2024, 1, 1, tzinfo=timezone.utc)
WINDOW_A_END   = datetime(2024, 1, 15, tzinfo=timezone.utc)
WINDOW_B_START = datetime(2024, 2, 1, tzinfo=timezone.utc)
WINDOW_B_END   = datetime(2024, 2, 15, tzinfo=timezone.utc)


def test_compare_returns_correct_run_counts(hist_file):
    _write(hist_file, [
        _entry("etl", True,  "2024-01-05T00:00:00+00:00"),
        _entry("etl", False, "2024-01-10T00:00:00+00:00"),
        _entry("etl", True,  "2024-02-03T00:00:00+00:00"),
        _entry("etl", True,  "2024-02-04T00:00:00+00:00"),
        _entry("etl", True,  "2024-02-05T00:00:00+00:00"),
    ])
    result = compare_pipeline(
        "etl", str(hist_file),
        WINDOW_A_START, WINDOW_A_END,
        WINDOW_B_START, WINDOW_B_END,
    )
    assert result.window_a_runs == 2
    assert result.window_b_runs == 3


def test_compare_success_rate_delta(hist_file):
    _write(hist_file, [
        _entry("etl", True,  "2024-01-05T00:00:00+00:00"),
        _entry("etl", False, "2024-01-06T00:00:00+00:00"),  # 50 %
        _entry("etl", True,  "2024-02-03T00:00:00+00:00"),
        _entry("etl", True,  "2024-02-04T00:00:00+00:00"),  # 100 %
    ])
    result = compare_pipeline(
        "etl", str(hist_file),
        WINDOW_A_START, WINDOW_A_END,
        WINDOW_B_START, WINDOW_B_END,
    )
    assert result.success_rate_delta == pytest.approx(50.0)


def test_compare_duration_delta(hist_file):
    _write(hist_file, [
        _entry("etl", True, "2024-01-05T00:00:00+00:00", duration=2.0),
        _entry("etl", True, "2024-02-03T00:00:00+00:00", duration=4.0),
    ])
    result = compare_pipeline(
        "etl", str(hist_file),
        WINDOW_A_START, WINDOW_A_END,
        WINDOW_B_START, WINDOW_B_END,
    )
    assert result.duration_delta == pytest.approx(2.0)


def test_duration_delta_none_when_no_runs(hist_file):
    hist_file.write_text("")
    result = compare_pipeline(
        "etl", str(hist_file),
        WINDOW_A_START, WINDOW_A_END,
        WINDOW_B_START, WINDOW_B_END,
    )
    assert result.duration_delta is None


def test_format_compare_text_contains_pipeline_name(hist_file):
    hist_file.write_text("")
    result = compare_pipeline(
        "my_pipeline", str(hist_file),
        WINDOW_A_START, WINDOW_A_END,
        WINDOW_B_START, WINDOW_B_END,
    )
    text = format_compare_text(result)
    assert "my_pipeline" in text
    assert "delta" in text
