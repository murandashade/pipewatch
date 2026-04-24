"""Tests for pipewatch.cli_health.handle_health."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from pipewatch.cli_health import handle_health


@pytest.fixture()
def config_file(tmp_path: Path) -> str:
    cfg = {
        "pipelines": [
            {"name": "pipe_a", "command": "echo a"},
            {"name": "pipe_b", "command": "echo b"},
        ]
    }
    p = tmp_path / "pipewatch.json"
    p.write_text(json.dumps(cfg))
    return str(p)


@pytest.fixture()
def hist_file(tmp_path: Path) -> str:
    entries = [
        {"pipeline": "pipe_a", "success": True},
        {"pipeline": "pipe_a", "success": False},
        {"pipeline": "pipe_b", "success": True},
    ]
    p = tmp_path / "history.json"
    p.write_text(json.dumps(entries))
    return str(p)


def _args(config, history, **kwargs):
    defaults = dict(
        config=config,
        history=history,
        baseline=".pipewatch_baseline.json",
        mute_file=".pipewatch_mute.json",
        window=10,
        pipeline=None,
        as_json=False,
        min_grade=None,
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_returns_zero_on_success(config_file, hist_file):
    rc = handle_health(_args(config_file, hist_file))
    assert rc == 0


def test_missing_config_returns_two(tmp_path, hist_file):
    rc = handle_health(_args(str(tmp_path / "missing.json"), hist_file))
    assert rc == 2


def test_json_output(config_file, hist_file, capsys):
    rc = handle_health(_args(config_file, hist_file, as_json=True))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list)
    assert all("score" in item for item in data)


def test_single_pipeline_filter(config_file, hist_file, capsys):
    rc = handle_health(_args(config_file, hist_file, pipeline="pipe_a", as_json=True))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert len(data) == 1
    assert data[0]["pipeline"] == "pipe_a"


def test_min_grade_filter(config_file, hist_file, capsys):
    # pipe_a has a failure so grade may be lower; request only D or worse
    rc = handle_health(_args(config_file, hist_file, min_grade="D", as_json=True))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    grades = ["A", "B", "C", "D", "F"]
    for item in data:
        assert grades.index(item["grade"]) >= grades.index("D")


def test_text_output_contains_grade(config_file, hist_file, capsys):
    handle_health(_args(config_file, hist_file))
    out = capsys.readouterr().out
    assert any(g in out for g in ["A", "B", "C", "D", "F"])
