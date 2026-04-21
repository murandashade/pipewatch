"""Tests for pipewatch.pipeline_status"""

import json
from pathlib import Path

import pytest

from pipewatch.pipeline_status import (
    pipeline_status,
    all_pipeline_statuses,
    format_status_text,
)


@pytest.fixture()
def hist_file(tmp_path):
    return tmp_path / "history.jsonl"


@pytest.fixture()
def mute_file(tmp_path):
    return tmp_path / "mute.json"


@pytest.fixture()
def baseline_file(tmp_path):
    return tmp_path / "baseline.json"


def _write(path, entries):
    with path.open("w") as fh:
        for e in entries:
            fh.write(json.dumps(e) + "\n")


def test_no_history_returns_defaults(hist_file, mute_file, baseline_file):
    s = pipeline_status("etl", hist_file, mute_file, baseline_file)
    assert s.name == "etl"
    assert s.last_run is None
    assert s.last_outcome is None
    assert s.failure_streak == 0
    assert s.muted is False


def test_last_outcome_from_history(hist_file, mute_file, baseline_file):
    _write(hist_file, [
        {"pipeline": "etl", "outcome": "success", "timestamp": "2024-01-01T00:00:00Z", "duration": 1.0},
        {"pipeline": "etl", "outcome": "failure", "timestamp": "2024-01-02T00:00:00Z", "duration": 0.5},
    ])
    s = pipeline_status("etl", hist_file, mute_file, baseline_file)
    assert s.last_outcome == "failure"
    assert s.failure_streak == 1


def test_muted_flag_reflected(hist_file, mute_file, baseline_file):
    mute_file.write_text(json.dumps({"etl": {"until": None}}))
    s = pipeline_status("etl", hist_file, mute_file, baseline_file)
    assert s.muted is True


def test_baseline_included(hist_file, mute_file, baseline_file):
    baseline_file.write_text(json.dumps({"etl": 42.5}))
    s = pipeline_status("etl", hist_file, mute_file, baseline_file)
    assert s.baseline_seconds == 42.5


def test_all_pipeline_statuses_length(hist_file, mute_file, baseline_file):
    result = all_pipeline_statuses(
        ["a", "b", "c"], hist_file, mute_file, baseline_file
    )
    assert len(result) == 3
    assert [r.name for r in result] == ["a", "b", "c"]


def test_format_status_text_no_pipelines():
    assert format_status_text([]) == "No pipelines configured."


def test_format_status_text_contains_name(hist_file, mute_file, baseline_file):
    statuses = all_pipeline_statuses(["my_pipeline"], hist_file, mute_file, baseline_file)
    text = format_status_text(statuses)
    assert "my_pipeline" in text
    assert "never" in text
