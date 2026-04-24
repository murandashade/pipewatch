"""Tests for pipewatch.history."""
import json
import os
import pytest

from pipewatch.history import (
    record_run,
    load_history,
    last_failure,
    failure_streak,
)


@pytest.fixture
def hist_file(tmp_path):
    return str(tmp_path / "history.json")


def test_record_run_creates_file(hist_file):
    rec = record_run("etl", True, 0, 1.23, hist_file)
    assert os.path.exists(hist_file)
    assert rec["pipeline"] == "etl"
    assert rec["success"] is True
    assert rec["exit_code"] == 0
    assert rec["duration_seconds"] == 1.23


def test_record_run_includes_timestamp(hist_file):
    """Each recorded run should include a timestamp field."""
    rec = record_run("etl", True, 0, 1.0, hist_file)
    assert "timestamp" in rec
    assert isinstance(rec["timestamp"], str)
    assert len(rec["timestamp"]) > 0


def test_record_run_appends(hist_file):
    record_run("etl", True, 0, 1.0, hist_file)
    record_run("etl", False, 1, 2.0, hist_file)
    entries = load_history(hist_file)
    assert len(entries) == 2


def test_load_history_missing_file(hist_file):
    assert load_history(hist_file) == []


def test_last_failure_returns_most_recent(hist_file):
    record_run("etl", False, 1, 0.5, hist_file)
    record_run("etl", True, 0, 0.5, hist_file)
    record_run("etl", False, 2, 0.5, hist_file)
    result = last_failure("etl", hist_file)
    assert result is not None
    assert result["exit_code"] == 2


def test_last_failure_none_when_all_pass(hist_file):
    record_run("etl", True, 0, 1.0, hist_file)
    assert last_failure("etl", hist_file) is None


def test_last_failure_unknown_pipeline(hist_file):
    """last_failure should return None for a pipeline with no recorded runs."""
    record_run("etl", False, 1, 1.0, hist_file)
    assert last_failure("other", hist_file) is None


def test_failure_streak_consecutive(hist_file):
    record_run("etl", True, 0, 1.0, hist_file)
    record_run("etl", False, 1, 1.0, hist_file)
    record_run("etl", False, 1, 1.0, hist_file)
    assert failure_streak("etl", hist_file) == 2


def test_failure_streak_reset_by_success(hist_file):
    record_run("etl", False, 1, 1.0, hist_file)
    record_run("etl", True, 0, 1.0, hist_file)
    assert failure_streak("etl", hist_file) == 0


def test_failure_streak_independent_pipelines(hist_file):
    record_run("etl", False, 1, 1.0, hist_file)
    record_run("other", False, 1, 1.0, hist_file)
    assert failure_streak("etl", hist_file) == 1
    assert failure_streak("other", hist_file) == 1
