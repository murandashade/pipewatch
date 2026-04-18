"""Tests for pipewatch.metrics."""
import json
import pytest
from pathlib import Path

from pipewatch.metrics import compute_metrics, format_metrics_text


@pytest.fixture()
def hist_file(tmp_path: Path) -> Path:
    return tmp_path / "history.jsonl"


def _write(path: Path, records: list) -> None:
    with path.open("w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def test_empty_history_returns_zero_runs(hist_file):
    hist_file.write_text("")
    m = compute_metrics(str(hist_file), "etl")
    assert m.total_runs == 0
    assert m.success_rate is None
    assert m.avg_duration_s is None


def test_counts_success_and_failure(hist_file):
    _write(hist_file, [
        {"pipeline": "etl", "success": True, "duration_s": 1.0},
        {"pipeline": "etl", "success": False, "duration_s": 2.0},
        {"pipeline": "etl", "success": True, "duration_s": 3.0},
    ])
    m = compute_metrics(str(hist_file), "etl")
    assert m.total_runs == 3
    assert m.success_count == 2
    assert m.failure_count == 1


def test_success_rate(hist_file):
    _write(hist_file, [
        {"pipeline": "etl", "success": True, "duration_s": 1.0},
        {"pipeline": "etl", "success": False, "duration_s": 1.0},
    ])
    m = compute_metrics(str(hist_file), "etl")
    assert m.success_rate == pytest.approx(0.5)


def test_duration_stats(hist_file):
    _write(hist_file, [
        {"pipeline": "etl", "success": True, "duration_s": 2.0},
        {"pipeline": "etl", "success": True, "duration_s": 4.0},
    ])
    m = compute_metrics(str(hist_file), "etl")
    assert m.avg_duration_s == pytest.approx(3.0)
    assert m.min_duration_s == pytest.approx(2.0)
    assert m.max_duration_s == pytest.approx(4.0)


def test_filters_other_pipelines(hist_file):
    _write(hist_file, [
        {"pipeline": "etl", "success": True, "duration_s": 1.0},
        {"pipeline": "other", "success": False, "duration_s": 5.0},
    ])
    m = compute_metrics(str(hist_file), "etl")
    assert m.total_runs == 1


def test_format_metrics_text(hist_file):
    _write(hist_file, [
        {"pipeline": "etl", "success": True, "duration_s": 1.5},
    ])
    m = compute_metrics(str(hist_file), "etl")
    text = format_metrics_text(m)
    assert "etl" in text
    assert "100.0%" in text
    assert "1.50s" in text
