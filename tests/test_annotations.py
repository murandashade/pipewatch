"""Tests for pipewatch.annotations."""
import json
import pytest
from pathlib import Path
from pipewatch.annotations import (
    add_annotation,
    get_annotations,
    delete_annotations,
    format_annotations_text,
)


@pytest.fixture
def ann_file(tmp_path):
    return tmp_path / "annotations.json"


def test_add_annotation_creates_file(ann_file):
    entry = add_annotation(ann_file, "pipe1", "looks good")
    assert ann_file.exists()
    assert entry["note"] == "looks good"
    assert "timestamp" in entry


def test_add_annotation_appends(ann_file):
    add_annotation(ann_file, "pipe1", "first")
    add_annotation(ann_file, "pipe1", "second")
    notes = get_annotations(ann_file, "pipe1")
    assert len(notes) == 2
    assert notes[1]["note"] == "second"


def test_get_annotations_missing_file(ann_file):
    assert get_annotations(ann_file, "pipe1") == []


def test_get_annotations_unknown_pipeline(ann_file):
    add_annotation(ann_file, "pipe1", "note")
    assert get_annotations(ann_file, "other") == []


def test_delete_annotations_returns_count(ann_file):
    add_annotation(ann_file, "pipe1", "a")
    add_annotation(ann_file, "pipe1", "b")
    count = delete_annotations(ann_file, "pipe1")
    assert count == 2
    assert get_annotations(ann_file, "pipe1") == []


def test_delete_annotations_missing_pipeline(ann_file):
    assert delete_annotations(ann_file, "nope") == 0


def test_format_annotations_text_empty():
    assert format_annotations_text([]) == "No annotations."


def test_format_annotations_text_with_author():
    entries = [{"note": "ok", "author": "alice", "timestamp": "2024-01-01T00:00:00+00:00"}]
    text = format_annotations_text(entries)
    assert "alice" in text
    assert "ok" in text


def test_format_annotations_text_no_author():
    entries = [{"note": "check this", "author": "", "timestamp": "2024-01-01T00:00:00+00:00"}]
    text = format_annotations_text(entries)
    assert "(" not in text
    assert "check this" in text
