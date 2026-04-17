"""Tests for pipewatch.alert_policy."""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from pipewatch.alert_policy import AlertPolicy, should_alert
from pipewatch.history import record_run


@pytest.fixture()
def hist_file(tmp_path):
    return str(tmp_path / "history.json")


def _record(name, success, hist_file, minutes_ago=0):
    ts = (datetime.now(tz=timezone.utc) - timedelta(minutes=minutes_ago)).isoformat()
    record_run(name, success, "cmd", 0.1, hist_file, timestamp=ts)


def test_no_failures_no_alert(hist_file):
    _record("pipe", True, hist_file)
    policy = AlertPolicy(min_streak=1)
    assert should_alert("pipe", hist_file, policy) is False


def test_single_failure_meets_default_streak(hist_file):
    _record("pipe", False, hist_file)
    policy = AlertPolicy(min_streak=1)
    assert should_alert("pipe", hist_file, policy) is True


def test_streak_below_threshold_suppresses(hist_file):
    _record("pipe", False, hist_file)
    policy = AlertPolicy(min_streak=3)
    assert should_alert("pipe", hist_file, policy) is False


def test_streak_meets_threshold_alerts(hist_file):
    for _ in range(3):
        _record("pipe", False, hist_file)
    policy = AlertPolicy(min_streak=3)
    assert should_alert("pipe", hist_file, policy) is True


def test_cooldown_suppresses_recent_failure(hist_file):
    _record("pipe", False, hist_file, minutes_ago=2)
    policy = AlertPolicy(min_streak=1, cooldown_minutes=10)
    assert should_alert("pipe", hist_file, policy) is False


def test_cooldown_allows_old_failure(hist_file):
    _record("pipe", False, hist_file, minutes_ago=20)
    policy = AlertPolicy(min_streak=1, cooldown_minutes=10)
    assert should_alert("pipe", hist_file, policy) is True


def test_missing_history_no_alert(hist_file):
    policy = AlertPolicy(min_streak=1)
    assert should_alert("pipe", hist_file, policy) is False
