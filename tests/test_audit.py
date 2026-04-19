"""Tests for pipewatch.audit."""
import json
import os
import pytest

from pipewatch.audit import (
    record_event,
    load_events,
    events_for_pipeline,
    format_audit_text,
)


@pytest.fixture()
def audit_file(tmp_path):
    return str(tmp_path / "audit.jsonl")


def test_record_event_creates_file(audit_file):
    record_event(audit_file, "mute", "etl_load", "muted for 60 min")
    assert os.path.exists(audit_file)


def test_record_event_returns_dict(audit_file):
    entry = record_event(audit_file, "config_change", "etl_load", "webhook updated")
    assert entry["event_type"] == "config_change"
    assert entry["pipeline"] == "etl_load"
    assert entry["detail"] == "webhook updated"
    assert "timestamp" in entry
    assert "actor" in entry


def test_record_event_appends(audit_file):
    record_event(audit_file, "mute", "p1", "muted")
    record_event(audit_file, "unmute", "p1", "unmuted")
    events = load_events(audit_file)
    assert len(events) == 2
    assert events[0]["event_type"] == "mute"
    assert events[1]["event_type"] == "unmute"


def test_load_events_missing_file(audit_file):
    result = load_events(audit_file)
    assert result == []


def test_events_for_pipeline_filters(audit_file):
    record_event(audit_file, "mute", "alpha", "muted")
    record_event(audit_file, "mute", "beta", "muted")
    record_event(audit_file, "unmute", "alpha", "unmuted")
    result = events_for_pipeline(audit_file, "alpha")
    assert len(result) == 2
    assert all(e["pipeline"] == "alpha" for e in result)


def test_events_for_pipeline_no_match(audit_file):
    record_event(audit_file, "mute", "alpha", "muted")
    assert events_for_pipeline(audit_file, "gamma") == []


def test_format_audit_text_empty():
    assert format_audit_text([]) == "No audit events found."


def test_format_audit_text_contains_fields(audit_file):
    entry = record_event(audit_file, "config_change", "etl", "schedule updated", actor="ci")
    text = format_audit_text([entry])
    assert "config_change" in text
    assert "etl" in text
    assert "schedule updated" in text
    assert "ci" in text
