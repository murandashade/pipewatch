"""Tests for pipewatch.pipeline_trends."""
import json
import pytest
from pathlib import Path

from pipewatch.pipeline_trends import (
    compute_trend,
    format_trend_text,
    PipelineTrend,
)


@pytest.fixture()
def hist_file(tmp_path: Path) -> Path:
    return tmp_path / "history.json"


def _write(hist_file: Path, entries: list) -> None:
    hist_file.write_text(json.dumps(entries))


def _entry(pipeline: str, success: bool, duration: float, ts: str) -> dict:
    return {
        "pipeline": pipeline,
        "success": success,
        "duration_seconds": duration,
        "timestamp": ts,
    }


def test_empty_history_returns_stable(hist_file):
    _write(hist_file, [])
    trend = compute_trend("pipe_a", str(hist_file))
    assert trend.pipeline == "pipe_a"
    assert trend.points == []
    assert trend.direction == "stable"
    assert trend.success_rate == 0.0


def test_all_successes_gives_full_rate(hist_file):
    entries = [
        _entry("pipe_a", True, 1.0, f"2024-01-01T00:0{i}:00+00:00")
        for i in range(5)
    ]
    _write(hist_file, entries)
    trend = compute_trend("pipe_a", str(hist_file))
    assert trend.success_rate == 1.0


def test_all_failures_gives_zero_rate(hist_file):
    entries = [
        _entry("pipe_a", False, 2.0, f"2024-01-01T00:0{i}:00+00:00")
        for i in range(5)
    ]
    _write(hist_file, entries)
    trend = compute_trend("pipe_a", str(hist_file))
    assert trend.success_rate == 0.0


def test_avg_duration_computed(hist_file):
    entries = [
        _entry("pipe_a", True, float(d), f"2024-01-01T00:0{i}:00+00:00")
        for i, d in enumerate([2, 4, 6])
    ]
    _write(hist_file, entries)
    trend = compute_trend("pipe_a", str(hist_file))
    assert trend.avg_duration == pytest.approx(4.0)


def test_direction_improving(hist_file):
    # first half: all fail, second half: all succeed
    entries = [
        _entry("pipe_a", False, 1.0, f"2024-01-01T00:0{i}:00+00:00") for i in range(4)
    ] + [
        _entry("pipe_a", True, 1.0, f"2024-01-01T01:0{i}:00+00:00") for i in range(4)
    ]
    _write(hist_file, entries)
    trend = compute_trend("pipe_a", str(hist_file))
    assert trend.direction == "improving"


def test_direction_degrading(hist_file):
    entries = [
        _entry("pipe_a", True, 1.0, f"2024-01-01T00:0{i}:00+00:00") for i in range(4)
    ] + [
        _entry("pipe_a", False, 1.0, f"2024-01-01T01:0{i}:00+00:00") for i in range(4)
    ]
    _write(hist_file, entries)
    trend = compute_trend("pipe_a", str(hist_file))
    assert trend.direction == "degrading"


def test_window_limits_entries(hist_file):
    entries = [
        _entry("pipe_a", True, 1.0, f"2024-01-{i+1:02d}T00:00:00+00:00")
        for i in range(30)
    ]
    _write(hist_file, entries)
    trend = compute_trend("pipe_a", str(hist_file), window=10)
    assert len(trend.points) == 10


def test_since_filter(hist_file):
    entries = [
        _entry("pipe_a", True, 1.0, "2024-01-01T00:00:00+00:00"),
        _entry("pipe_a", False, 1.0, "2024-06-01T00:00:00+00:00"),
    ]
    _write(hist_file, entries)
    trend = compute_trend("pipe_a", str(hist_file), since="2024-03-01T00:00:00+00:00")
    assert len(trend.points) == 1
    assert trend.points[0].success is False


def test_format_trend_text(hist_file):
    _write(hist_file, [_entry("pipe_a", True, 3.0, "2024-01-01T00:00:00+00:00")])
    trend = compute_trend("pipe_a", str(hist_file))
    text = format_trend_text(trend)
    assert "pipe_a" in text
    assert "100.0%" in text
    assert "stable" in text
