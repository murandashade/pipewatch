"""Tests for pipewatch.cli_metrics."""
import json
import argparse
from pathlib import Path

import pytest

from pipewatch.cli_metrics import handle_metrics


@pytest.fixture()
def hist_file(tmp_path: Path) -> Path:
    return tmp_path / "history.jsonl"


def _write(path: Path, records: list) -> None:
    with path.open("w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def _args(hist: str, pipeline: str = "etl", as_json: bool = False) -> argparse.Namespace:
    return argparse.Namespace(history=hist, pipeline=pipeline, json=as_json)


def test_missing_history_returns_two(tmp_path):
    args = _args(str(tmp_path / "nope.jsonl"))
    assert handle_metrics(args) == 2


def test_returns_zero_on_success(hist_file):
    _write(hist_file, [{"pipeline": "etl", "success": True, "duration_s": 1.0}])
    assert handle_metrics(_args(str(hist_file))) == 0


def test_text_output_contains_pipeline(hist_file, capsys):
    _write(hist_file, [{"pipeline": "etl", "success": True, "duration_s": 2.0}])
    handle_metrics(_args(str(hist_file)))
    out = capsys.readouterr().out
    assert "etl" in out
    assert "100.0%" in out


def test_json_output_is_valid(hist_file, capsys):
    _write(hist_file, [
        {"pipeline": "etl", "success": True, "duration_s": 1.0},
        {"pipeline": "etl", "success": False, "duration_s": 2.0},
    ])
    handle_metrics(_args(str(hist_file), as_json=True))
    data = json.loads(capsys.readouterr().out)
    assert data["total_runs"] == 2
    assert data["success_count"] == 1
    assert data["success_rate"] == pytest.approx(0.5)


def test_empty_pipeline_shows_zero(hist_file, capsys):
    hist_file.write_text("")
    handle_metrics(_args(str(hist_file)))
    out = capsys.readouterr().out
    assert "0" in out
