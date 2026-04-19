"""Tests for pipewatch.mute."""

from datetime import datetime, timezone, timedelta
from pathlib import Path
import pytest

import pipewatch.mute as mute_mod


@pytest.fixture()
def state_file(tmp_path):
    return tmp_path / "mute.json"


def test_not_muted_when_no_state(state_file):
    assert mute_mod.is_muted("pipe_a", path=state_file) is False


def test_mute_makes_pipeline_muted(state_file):
    mute_mod.mute_pipeline("pipe_a", hours=2, path=state_file)
    assert mute_mod.is_muted("pipe_a", path=state_file) is True


def test_mute_does_not_affect_other_pipelines(state_file):
    mute_mod.mute_pipeline("pipe_a", hours=2, path=state_file)
    assert mute_mod.is_muted("pipe_b", path=state_file) is False


def test_expired_mute_returns_false(monkeypatch, state_file):
    mute_mod.mute_pipeline("pipe_a", hours=1, path=state_file)
    future = datetime.now(timezone.utc) + timedelta(hours=2)
    monkeypatch.setattr(mute_mod, "_utcnow", lambda: future)
    assert mute_mod.is_muted("pipe_a", path=state_file) is False


def test_unmute_removes_entry(state_file):
    mute_mod.mute_pipeline("pipe_a", hours=2, path=state_file)
    result = mute_mod.unmute_pipeline("pipe_a", path=state_file)
    assert result is True
    assert mute_mod.is_muted("pipe_a", path=state_file) is False


def test_unmute_returns_false_when_not_muted(state_file):
    assert mute_mod.unmute_pipeline("pipe_a", path=state_file) is False


def test_muted_until_returns_timestamp(state_file):
    mute_mod.mute_pipeline("pipe_a", hours=3, path=state_file)
    ts = mute_mod.muted_until("pipe_a", path=state_file)
    assert ts is not None
    parsed = datetime.fromisoformat(ts)
    assert parsed > datetime.now(timezone.utc)


def test_muted_until_returns_none_when_expired(monkeypatch, state_file):
    mute_mod.mute_pipeline("pipe_a", hours=1, path=state_file)
    future = datetime.now(timezone.utc) + timedelta(hours=2)
    monkeypatch.setattr(mute_mod, "_utcnow", lambda: future)
    assert mute_mod.muted_until("pipe_a", path=state_file) is None
