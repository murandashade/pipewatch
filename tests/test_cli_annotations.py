"""Tests for pipewatch.cli_annotations."""
import pytest
from pathlib import Path
from pipewatch.cli_annotations import handle_annotations


class _Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


@pytest.fixture
def ann_file(tmp_path):
    return tmp_path / "annotations.json"


def test_add_returns_zero(ann_file, capsys):
    args = _Args(file=str(ann_file), ann_cmd="add", pipeline="p1", note="hello", author="")
    assert handle_annotations(args) == 0
    out = capsys.readouterr().out
    assert "added" in out


def test_show_empty(ann_file, capsys):
    args = _Args(file=str(ann_file), ann_cmd="show", pipeline="p1")
    assert handle_annotations(args) == 0
    assert "No annotations" in capsys.readouterr().out


def test_show_after_add(ann_file, capsys):
    add_args = _Args(file=str(ann_file), ann_cmd="add", pipeline="p1", note="test note", author="bob")
    handle_annotations(add_args)
    show_args = _Args(file=str(ann_file), ann_cmd="show", pipeline="p1")
    handle_annotations(show_args)
    assert "test note" in capsys.readouterr().out


def test_delete_returns_zero(ann_file, capsys):
    add_args = _Args(file=str(ann_file), ann_cmd="add", pipeline="p1", note="x", author="")
    handle_annotations(add_args)
    del_args = _Args(file=str(ann_file), ann_cmd="delete", pipeline="p1")
    assert handle_annotations(del_args) == 0
    assert "1" in capsys.readouterr().out


def test_unknown_cmd_returns_two(ann_file, capsys):
    args = _Args(file=str(ann_file), ann_cmd="bogus")
    assert handle_annotations(args) == 2
