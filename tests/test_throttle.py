"""Tests for pipewatch.throttle."""
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from pipewatch.throttle import is_throttled, record_alert, clear_throttle, _STATE_FILE


@pytest.fixture()
def state_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write_state(state_dir: Path, name: str, dt: datetime) -> None:
    path = state_dir / _STATE_FILE
    data = json.loads(path.read_text()) if path.exists() else {}
    data[name] = dt.isoformat()
    path.write_text(json.dumps(data))


def test_not_throttled_when_no_state(state_dir):
    assert is_throttled("pipe_a", 300, state_dir=str(state_dir)) is False


def test_throttled_within_window(state_dir):
    now = datetime.now(timezone.utc)
    _write_state(state_dir, "pipe_a", now - timedelta(seconds=60))
    assert is_throttled("pipe_a", 300, state_dir=str(state_dir)) is True


def test_not_throttled_after_window_expires(state_dir):
    now = datetime.now(timezone.utc)
    _write_state(state_dir, "pipe_a", now - timedelta(seconds=400))
    assert is_throttled("pipe_a", 300, state_dir=str(state_dir)) is False


def test_record_alert_creates_state(state_dir):
    record_alert("pipe_b", state_dir=str(state_dir))
    assert is_throttled("pipe_b", 300, state_dir=str(state_dir)) is True


def test_record_alert_updates_existing(state_dir):
    old = datetime.now(timezone.utc) - timedelta(seconds=500)
    _write_state(state_dir, "pipe_b", old)
    record_alert("pipe_b", state_dir=str(state_dir))
    assert is_throttled("pipe_b", 300, state_dir=str(state_dir)) is True


def test_clear_throttle_removes_entry(state_dir):
    record_alert("pipe_c", state_dir=str(state_dir))
    clear_throttle("pipe_c", state_dir=str(state_dir))
    assert is_throttled("pipe_c", 300, state_dir=str(state_dir)) is False


def test_clear_throttle_missing_name_is_noop(state_dir):
    clear_throttle("nonexistent", state_dir=str(state_dir))  # should not raise


def test_corrupt_state_file_treated_as_empty(state_dir):
    (state_dir / _STATE_FILE).write_text("not json")
    assert is_throttled("pipe_a", 300, state_dir=str(state_dir)) is False
