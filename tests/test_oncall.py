import pytest
from pipewatch.oncall import (
    set_oncall, get_oncall, remove_oncall, format_oncall_text,
    _load,
)


@pytest.fixture
def oc_file(tmp_path):
    return str(tmp_path / "oncall.json")


def test_get_oncall_missing_file_returns_empty(oc_file):
    result = get_oncall("etl", path=oc_file)
    assert result == []


def test_set_and_get_oncall(oc_file):
    set_oncall("etl", "alice@example.com", path=oc_file)
    result = get_oncall("etl", path=oc_file)
    assert len(result) == 1
    assert result[0]["contact"] == "alice@example.com"
    assert result[0]["pipeline"] == "etl"


def test_set_oncall_overwrites(oc_file):
    set_oncall("etl", "alice@example.com", path=oc_file)
    set_oncall("etl", "bob@example.com", path=oc_file)
    result = get_oncall("etl", path=oc_file)
    assert len(result) == 1
    assert result[0]["contact"] == "bob@example.com"


def test_set_oncall_multiple_pipelines(oc_file):
    set_oncall("etl", "alice@example.com", path=oc_file)
    set_oncall("reports", "bob@example.com", path=oc_file)
    assert get_oncall("etl", path=oc_file)[0]["contact"] == "alice@example.com"
    assert get_oncall("reports", path=oc_file)[0]["contact"] == "bob@example.com"


def test_remove_oncall_existing(oc_file):
    set_oncall("etl", "alice@example.com", path=oc_file)
    removed = remove_oncall("etl", path=oc_file)
    assert removed is True
    assert get_oncall("etl", path=oc_file) == []


def test_remove_oncall_missing(oc_file):
    removed = remove_oncall("ghost", path=oc_file)
    assert removed is False


def test_format_oncall_text():
    entry = {"pipeline": "etl", "contact": "ops@example.com", "set_at": "2024-01-01T00:00:00"}
    text = format_oncall_text(entry)
    assert "ops@example.com" in text
    assert "etl" in text
