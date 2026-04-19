import json
import pytest
from pipewatch.runbook import (
    add_runbook, get_runbooks, remove_runbook, all_runbooks, format_runbooks_text
)


@pytest.fixture
def rb_file(tmp_path):
    return str(tmp_path / "runbooks.json")


def test_add_runbook_creates_entry(rb_file):
    entry = add_runbook("etl", "https://wiki/etl", note="fix guide", path=rb_file)
    assert entry["url"] == "https://wiki/etl"
    assert entry["note"] == "fix guide"


def test_get_runbooks_returns_entries(rb_file):
    add_runbook("etl", "https://wiki/etl", path=rb_file)
    add_runbook("etl", "https://wiki/etl2", path=rb_file)
    books = get_runbooks("etl", path=rb_file)
    assert len(books) == 2


def test_get_runbooks_missing_pipeline(rb_file):
    assert get_runbooks("nope", path=rb_file) == []


def test_remove_runbook_existing(rb_file):
    add_runbook("etl", "https://wiki/etl", path=rb_file)
    removed = remove_runbook("etl", "https://wiki/etl", path=rb_file)
    assert removed is True
    assert get_runbooks("etl", path=rb_file) == []


def test_remove_runbook_nonexistent(rb_file):
    assert remove_runbook("etl", "https://missing", path=rb_file) is False


def test_all_runbooks(rb_file):
    add_runbook("a", "https://a", path=rb_file)
    add_runbook("b", "https://b", path=rb_file)
    data = all_runbooks(path=rb_file)
    assert "a" in data and "b" in data


def test_format_runbooks_text_with_entries():
    entries = [{"url": "https://wiki", "note": "check logs"}]
    text = format_runbooks_text("etl", entries)
    assert "https://wiki" in text
    assert "check logs" in text


def test_format_runbooks_text_empty():
    text = format_runbooks_text("etl", [])
    assert "No runbooks" in text
