"""Tests for pipewatch.pipeline_health."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipewatch.pipeline_health import (
    HealthScore,
    _grade,
    compute_health,
    all_health_scores,
    format_health_text,
)


@pytest.fixture()
def hist_file(tmp_path: Path) -> str:
    return str(tmp_path / "history.json")


@pytest.fixture()
def baseline_file(tmp_path: Path) -> str:
    return str(tmp_path / "baseline.json")


@pytest.fixture()
def mute_file(tmp_path: Path) -> str:
    return str(tmp_path / "mute.json")


def _write(path: str, data) -> None:
    Path(path).write_text(json.dumps(data))


def test_grade_boundaries():
    assert _grade(100) == "A"
    assert _grade(90) == "A"
    assert _grade(89) == "B"
    assert _grade(75) == "B"
    assert _grade(74) == "C"
    assert _grade(60) == "C"
    assert _grade(59) == "D"
    assert _grade(40) == "D"
    assert _grade(39) == "F"
    assert _grade(0) == "F"


def test_no_history_returns_score_50(hist_file, baseline_file, mute_file):
    score = compute_health("pipe_a", hist_file, baseline_file, mute_file)
    assert score.score == 50
    assert score.total_runs == 0
    assert score.recent_failures == 0


def test_all_successes_scores_100(hist_file, baseline_file, mute_file):
    entries = [{"pipeline": "p", "success": True, "duration_seconds": 1.0} for _ in range(5)]
    _write(hist_file, entries)
    score = compute_health("p", hist_file, baseline_file, mute_file)
    assert score.score == 100
    assert score.grade == "A"


def test_all_failures_scores_zero(hist_file, baseline_file, mute_file):
    entries = [{"pipeline": "p", "success": False} for _ in range(5)]
    _write(hist_file, entries)
    score = compute_health("p", hist_file, baseline_file, mute_file)
    assert score.score == 0
    assert score.grade == "F"


def test_partial_failures_scored_correctly(hist_file, baseline_file, mute_file):
    entries = (
        [{"pipeline": "p", "success": True}] * 8
        + [{"pipeline": "p", "success": False}] * 2
    )
    _write(hist_file, entries)
    score = compute_health("p", hist_file, baseline_file, mute_file)
    assert score.score == 80
    assert score.recent_failures == 2


def test_slow_pipeline_deducts_points(hist_file, baseline_file, mute_file):
    entries = [{"pipeline": "p", "success": True, "duration_seconds": 30.0}]
    _write(hist_file, entries)
    _write(baseline_file, {"p": 10.0})  # 30 > 10 * 1.5 => slow
    score = compute_health("p", hist_file, baseline_file, mute_file)
    assert score.is_slow is True
    assert score.score == 90  # 100 - 10


def test_muted_pipeline_reflected_in_score(hist_file, baseline_file, mute_file, tmp_path):
    from datetime import datetime, timezone, timedelta
    until = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    _write(mute_file, {"p": {"muted_until": until}})
    entries = [{"pipeline": "p", "success": True}]
    _write(hist_file, entries)
    score = compute_health("p", hist_file, baseline_file, mute_file)
    assert score.is_muted is True


def test_all_health_scores_returns_list(hist_file, baseline_file, mute_file):
    scores = all_health_scores(["a", "b"], hist_file, baseline_file, mute_file)
    assert len(scores) == 2
    assert {s.pipeline for s in scores} == {"a", "b"}


def test_format_health_text_empty():
    text = format_health_text([])
    assert "No pipeline" in text


def test_format_health_text_contains_pipeline(hist_file, baseline_file, mute_file):
    scores = all_health_scores(["my_pipeline"], hist_file, baseline_file, mute_file)
    text = format_health_text(scores)
    assert "my_pipeline" in text
