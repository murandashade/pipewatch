"""Tests for pipewatch configuration loading and validation."""

import json
import pytest
from pathlib import Path
from pipewatch.config import load_config, validate_config, AppConfig, PipelineConfig


@pytest.fixture
def config_file(tmp_path):
    def _write(data):
        p = tmp_path / "pipewatch.json"
        p.write_text(json.dumps(data))
        return str(p)
    return _write


def test_load_basic_config(config_file):
    path = config_file({
        "default_webhook_url": "https://hooks.example.com/abc",
        "pipelines": [
            {"name": "etl-daily", "alert_on": ["failure", "timeout"]}
        ]
    })
    config = load_config(path)
    assert len(config.pipelines) == 1
    assert config.pipelines[0].name == "etl-daily"
    assert config.pipelines[0].webhook_url == "https://hooks.example.com/abc"
    assert "timeout" in config.pipelines[0].alert_on


def test_pipeline_overrides_webhook(config_file):
    path = config_file({
        "default_webhook_url": "https://default.hook",
        "pipelines": [
            {"name": "custom", "webhook_url": "https://custom.hook"}
        ]
    })
    config = load_config(path)
    assert config.pipelines[0].webhook_url == "https://custom.hook"


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path/config.json")


def test_validate_missing_webhook():
    config = AppConfig(pipelines=[
        PipelineConfig(name="broken-pipe", webhook_url="")
    ])
    errors = validate_config(config)
    assert any("webhook_url" in e for e in errors)


def test_validate_unknown_event():
    config = AppConfig(pipelines=[
        PipelineConfig(name="pipe", webhook_url="https://hook", alert_on=["crash"])
    ])
    errors = validate_config(config)
    assert any("crash" in e for e in errors)


def test_validate_valid_config():
    config = AppConfig(pipelines=[
        PipelineConfig(name="pipe", webhook_url="https://hook", alert_on=["failure"])
    ])
    errors = validate_config(config)
    assert errors == []
