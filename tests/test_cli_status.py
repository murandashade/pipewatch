"""Tests for pipewatch.cli_status"""

import json
from pathlib import Path

import pytest

from pipewatch.cli_status import handle_status


@pytest.fixture()
def config_file(tmp_path):
    cfg = {
        "webhook_url": "https://hooks.example.com/test",
        "pipelines": [
            {"name": "alpha", "command": "echo alpha"},
            {"name": "beta", "command": "echo beta"},
        ],
    }
    p = tmp_path / "pipewatch.json"
    p.write_text(json.dumps(cfg))
    return p


class _Args:
    def __init__(self, config, tmp_path, pipeline=None, as_json=False):
        self.config = str(config)
        self.history_file = str(tmp_path / "history.jsonl")
        self.mute_file = str(tmp_path / "mute.json")
        self.baseline_file = str(tmp_path / "baseline.json")
        self.pipeline = pipeline
        self.json = as_json


def test_returns_zero_on_success(config_file, tmp_path, capsys):
    args = _Args(config_file, tmp_path)
    assert handle_status(args) == 0


def test_text_output_contains_pipeline_names(config_file, tmp_path, capsys):
    args = _Args(config_file, tmp_path)
    handle_status(args)
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out


def test_json_output_is_valid(config_file, tmp_path, capsys):
    args = _Args(config_file, tmp_path, as_json=True)
    handle_status(args)
    data = json.loads(capsys.readouterr().out)
    names = [d["name"] for d in data]
    assert "alpha" in names and "beta" in names


def test_filter_single_pipeline(config_file, tmp_path, capsys):
    args = _Args(config_file, tmp_path, pipeline="alpha", as_json=True)
    handle_status(args)
    data = json.loads(capsys.readouterr().out)
    assert len(data) == 1
    assert data[0]["name"] == "alpha"


def test_unknown_pipeline_returns_two(config_file, tmp_path):
    args = _Args(config_file, tmp_path, pipeline="ghost")
    assert handle_status(args) == 2


def test_missing_config_returns_two(tmp_path):
    args = _Args(tmp_path / "missing.json", tmp_path)
    assert handle_status(args) == 2
