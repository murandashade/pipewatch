"""Tests for pipewatch.notifier."""

from __future__ import annotations

import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from pipewatch.notifier import _state_path, is_on_cooldown, notify
from pipewatch.webhook import AlertPayload


@pytest.fixture()
def base_dir(tmp_path: Path) -> str:
    return str(tmp_path)


@pytest.fixture()
def payload() -> AlertPayload:
    return AlertPayload(
        pipeline_name="etl_daily",
        status="failure",
        message="Pipeline crashed",
        timestamp="2024-01-01T00:00:00Z",
    )


def _write_state(base_dir: str, name: str, last_sent: float) -> None:
    state_file = _state_path(base_dir, name)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps({"last_sent": last_sent}))


def test_not_on_cooldown_when_no_state(base_dir: str) -> None:
    assert is_on_cooldown("etl_daily", cooldown=300, base_dir=base_dir) is False


def test_on_cooldown_when_recently_notified(base_dir: str) -> None:
    _write_state(base_dir, "etl_daily", time.time() - 60)
    assert is_on_cooldown("etl_daily", cooldown=300, base_dir=base_dir) is True


def test_not_on_cooldown_after_window_expires(base_dir: str) -> None:
    _write_state(base_dir, "etl_daily", time.time() - 400)
    assert is_on_cooldown("etl_daily", cooldown=300, base_dir=base_dir) is False


def test_notify_sends_and_records_state(
    base_dir: str, payload: AlertPayload
) -> None:
    with patch("pipewatch.notifier.send_webhook") as mock_send:
        result = notify(payload, "https://hooks.example.com/x", cooldown=300, base_dir=base_dir)

    assert result is True
    mock_send.assert_called_once()
    state_file = _state_path(base_dir, payload.pipeline_name)
    assert state_file.exists()
    data = json.loads(state_file.read_text())
    assert "last_sent" in data


def test_notify_suppressed_on_cooldown(
    base_dir: str, payload: AlertPayload
) -> None:
    _write_state(base_dir, payload.pipeline_name, time.time() - 10)
    with patch("pipewatch.notifier.send_webhook") as mock_send:
        result = notify(payload, "https://hooks.example.com/x", cooldown=300, base_dir=base_dir)

    assert result is False
    mock_send.assert_not_called()


def test_notify_sends_after_cooldown_expires(
    base_dir: str, payload: AlertPayload
) -> None:
    _write_state(base_dir, payload.pipeline_name, time.time() - 400)
    with patch("pipewatch.notifier.send_webhook") as mock_send:
        result = notify(payload, "https://hooks.example.com/x", cooldown=300, base_dir=base_dir)

    assert result is True
    mock_send.assert_called_once()
