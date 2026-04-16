import sys
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from pipewatch.config import PipelineConfig
from pipewatch.monitor import RunResult, handle_result, run_pipeline


@pytest.fixture
def pipeline_cfg():
    return PipelineConfig(name="etl", command="echo hello", webhook_url="https://hooks.example.com/abc")


def test_run_pipeline_success():
    result = run_pipeline("test", "exit 0")
    assert result.success
    assert result.exit_code == 0
    assert result.pipeline_name == "test"
    assert result.duration_seconds >= 0


def test_run_pipeline_failure():
    result = run_pipeline("test", "exit 2")
    assert not result.success
    assert result.exit_code == 2


def test_run_pipeline_captures_stderr():
    result = run_pipeline("test", "echo error-msg >&2; exit 1")
    assert "error-msg" in result.stderr
    assert not result.success


def test_run_pipeline_timeout():
    result = run_pipeline("slow", "sleep 10", timeout=1)
    assert result.exit_code == -1
    assert "timed out" in result.stderr


def test_handle_result_no_alert_on_success(pipeline_cfg):
    result = RunResult(
        pipeline_name="etl", exit_code=0, stdout="ok", stderr="", duration_seconds=1.0
    )
    with patch("pipewatch.monitor.send_webhook") as mock_send:
        sent = handle_result(result, pipeline_cfg)
    assert not sent
    mock_send.assert_not_called()


def test_handle_result_sends_alert_on_failure(pipeline_cfg):
    result = RunResult(
        pipeline_name="etl", exit_code=1, stdout="", stderr="boom", duration_seconds=2.5
    )
    with patch("pipewatch.monitor.send_webhook") as mock_send:
        sent = handle_result(result, pipeline_cfg)
    assert sent
    mock_send.assert_called_once()
    args = mock_send.call_args[0]
    assert args[0] == pipeline_cfg.webhook_url
    assert args[1].error_output == "boom"


def test_handle_result_uses_default_webhook_when_none():
    cfg = PipelineConfig(name="etl", command="echo hi", webhook_url=None)
    result = RunResult(
        pipeline_name="etl", exit_code=1, stdout="", stderr="err", duration_seconds=0.1
    )
    with patch("pipewatch.monitor.send_webhook") as mock_send:
        sent = handle_result(result, cfg, default_webhook="https://default.hook/x")
    assert sent
    assert mock_send.call_args[0][0] == "https://default.hook/x"


def test_handle_result_no_webhook_skips_alert():
    cfg = PipelineConfig(name="etl", command="echo hi", webhook_url=None)
    result = RunResult(
        pipeline_name="etl", exit_code=1, stdout="", stderr="err", duration_seconds=0.1
    )
    with patch("pipewatch.monitor.send_webhook") as mock_send:
        sent = handle_result(result, cfg, default_webhook=None)
    assert not sent
    mock_send.assert_not_called()
