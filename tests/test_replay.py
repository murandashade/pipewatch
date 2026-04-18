"""Tests for pipewatch.replay."""
from __future__ import annotations

import json
import pathlib
import pytest

from pipewatch.config import PipelineConfig
from pipewatch.replay import failed_runs, replay_failures


@pytest.fixture()
def hist_file(tmp_path: pathlib.Path) -> pathlib.Path:
    return tmp_path / "history.jsonl"


def _write(path: pathlib.Path, entries: list) -> None:
    with path.open("w") as fh:
        for e in entries:
            fh.write(json.dumps(e) + "\n")


def _cfg(name: str, cmd: str = "true") -> PipelineConfig:
    return PipelineConfig(name=name, command=cmd)


def test_failed_runs_returns_only_failures(hist_file):
    _write(hist_file, [
        {"pipeline": "a", "success": True},
        {"pipeline": "b", "success": False},
        {"pipeline": "c", "success": False},
    ])
    result = failed_runs(str(hist_file))
    assert len(result) == 2
    assert all(not r["success"] for r in result)


def test_failed_runs_filters_by_name(hist_file):
    _write(hist_file, [
        {"pipeline": "a", "success": False},
        {"pipeline": "b", "success": False},
    ])
    result = failed_runs(str(hist_file), pipeline_name="a")
    assert len(result) == 1
    assert result[0]["pipeline"] == "a"


def test_failed_runs_empty_history(hist_file):
    _write(hist_file, [])
    assert failed_runs(str(hist_file)) == []


def test_failed_runs_missing_file(tmp_path):
    result = failed_runs(str(tmp_path / "no.jsonl"))
    assert result == []


def test_replay_failures_runs_failed_pipelines(hist_file):
    _write(hist_file, [
        {"pipeline": "ok", "success": True},
        {"pipeline": "bad", "success": False},
    ])
    configs = [_cfg("ok"), _cfg("bad", "true")]
    results = replay_failures(configs, str(hist_file))
    assert len(results) == 1
    assert results[0].pipeline == "bad"


def test_replay_failures_filter_by_name(hist_file):
    _write(hist_file, [
        {"pipeline": "x", "success": False},
        {"pipeline": "y", "success": False},
    ])
    configs = [_cfg("x", "true"), _cfg("y", "true")]
    results = replay_failures(configs, str(hist_file), pipeline_name="x")
    assert len(results) == 1
    assert results[0].pipeline == "x"


def test_replay_failures_no_failures(hist_file):
    _write(hist_file, [{"pipeline": "ok", "success": True}])
    configs = [_cfg("ok")]
    results = replay_failures(configs, str(hist_file))
    assert results == []
