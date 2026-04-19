"""Tests for pipewatch.oncall."""
import pytest

from pipewatch.oncall import (
    set_oncall,
    get_oncall,
    remove_oncall,
    all_oncall,
    format_oncall_text,
)


@pytest.fixture
def oc_file(tmp_path):
    return str(tmp_path / "oncall.json")


def test_get_oncall_missing_file_returns_empty(oc_file):
    assert get_oncall(oc_file, "pipe_a") == []


def test_set_and_get_oncall(oc_file):
    set_oncall(oc_file, "pipe_a", ["alice@example.com", "bob@example.com"])
    result = get_oncall(oc_file, "pipe_a")
    assert result == ["alice@example.com", "bob@example.com"]


def test_set_oncall_overwrites(oc_file):
    set_oncall(oc_file, "pipe_a", ["alice@example.com"])
    set_oncall(oc_file, "pipe_a", ["carol@example.com"])
    assert get_oncall(oc_file, "pipe_a") == ["carol@example.com"]


def test_set_oncall_multiple_pipelines(oc_file):
    set_oncall(oc_file, "pipe_a", ["alice@example.com"])
    set_oncall(oc_file, "pipe_b", ["bob@example.com"])
    assert get_oncall(oc_file, "pipe_a") == ["alice@example.com"]
    assert get_oncall(oc_file, "pipe_b") == ["bob@example.com"]


def test_remove_oncall_existing(oc_file):
    set_oncall(oc_file, "pipe_a", ["alice@example.com"])
    removed = remove_oncall(oc_file, "pipe_a")
    assert removed is True
    assert get_oncall(oc_file, "pipe_a") == []


def test_remove_oncall_nonexistent(oc_file):
    assert remove_oncall(oc_file, "pipe_a") is False


def test_all_oncall_returns_mapping(oc_file):
    set_oncall(oc_file, "pipe_a", ["alice@example.com"])
    set_oncall(oc_file, "pipe_b", ["bob@example.com"])
    mapping = all_oncall(oc_file)
    assert mapping == {
        "pipe_a": ["alice@example.com"],
        "pipe_b": ["bob@example.com"],
    }


def test_format_oncall_text_with_contacts():
    result = format_oncall_text("pipe_a", ["alice@example.com", "bob@example.com"])
    assert result == "pipe_a: alice@example.com, bob@example.com"


def test_format_oncall_text_empty_contacts():
    result = format_oncall_text("pipe_a", [])
    assert "no on-call" in result
