import json
import os
import tempfile
from unittest.mock import patch

import pytest

from pipewatch.runner import run_all, summarise
from pipewatch.monitor import RunResult


@pytest.fixture
def config_file():
    data = {
        "default_webhook_url": "https://hooks.example.com/default",
        "pipelines": [
            {"name": "ok-pipe", "command": "exit 0"},
            {"name": "fail-pipe", "command": "exit 1"},
        ],
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        yield f.name
    os.unlink(f.name)


def test_run_all_returns_results(config_file):
    with patch("pipewatch.runner.send_webhook", side_effect=None), \
         patch("pipewatch.monitor.send_webhook"):
        results = run_all(config_file)
    assert len(results) == 2
    names = {r.pipeline_name for r in results}
    assert "ok-pipe" in names
    assert "fail-pipe" in names


def test_run_all_correct_success_flags(config_file):
    with patch("pipewatch.monitor.send_webhook"):
        results = run_all(config_file)
    by_name = {r.pipeline_name: r for r in results}
    assert by_name["ok-pipe"].success
    assert not by_name["fail-pipe"].success


def test_run_all_sends_alert_for_failure(config_file):
    with patch("pipewatch.monitor.send_webhook") as mock_send:
        run_all(config_file)
    mock_send.assert_called_once()
    assert mock_send.call_args[0][0] == "https://hooks.example.com/default"


def test_summarise_all_pass():
    results = [
        RunResult("a", 0, "", "", 1.0),
        RunResult("b", 0, "", "", 2.0),
    ]
    assert summarise(results) == 0


def test_summarise_with_failures():
    results = [
        RunResult("a", 0, "", "", 1.0),
        RunResult("b", 1, "", "err", 0.5),
    ]
    assert summarise(results) == 1
