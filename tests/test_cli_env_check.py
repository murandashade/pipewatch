"""Tests for pipewatch.cli_env_check."""
import json
import os
import pytest
from unittest.mock import patch
from pathlib import Path
from pipewatch.cli_env_check import handle_env_check


@pytest.fixture
def config_file(tmp_path):
    cfg = tmp_path / "pipewatch.json"
    cfg.write_text(
        json.dumps({
            "webhook_url": "http://example.com/hook",
            "pipelines": [
                {"name": "pipe_a", "command": "echo a", "required_env": ["NEEDED_VAR"]},
                {"name": "pipe_b", "command": "echo b"},
            ],
        })
    )
    return cfg


class _Args:
    def __init__(self, config, as_json=False):
        self.config = str(config)
        self.as_json = as_json


def test_missing_config_returns_two(tmp_path):
    args = _Args(tmp_path / "nope.json")
    assert handle_env_check(args) == 2


def test_returns_zero_when_all_present(config_file):
    with patch.dict(os.environ, {"NEEDED_VAR": "yes"}):
        assert handle_env_check(_Args(config_file)) == 0


def test_returns_one_when_missing(config_file):
    env = {k: v for k, v in os.environ.items() if k != "NEEDED_VAR"}
    with patch.dict(os.environ, env, clear=True):
        assert handle_env_check(_Args(config_file)) == 1


def test_json_output(config_file, capsys):
    with patch.dict(os.environ, {"NEEDED_VAR": "yes"}):
        handle_env_check(_Args(config_file, as_json=True))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, list)
    assert data[0]["pipeline"] == "pipe_a"
    assert data[0]["ok"] is True


def test_text_output_contains_pipeline_name(config_file, capsys):
    with patch.dict(os.environ, {"NEEDED_VAR": "yes"}):
        handle_env_check(_Args(config_file))
    out = capsys.readouterr().out
    assert "pipe_a" in out
