import argparse
import pytest
from pipewatch.cli_snapshots import handle_snapshot


class _Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


@pytest.fixture
def sd(tmp_path):
    return str(tmp_path / "snaps")


def test_show_missing_returns_one(sd):
    args = _Args(snapshot_cmd="show", name="missing", snapshot_dir=sd)
    assert handle_snapshot(args) == 1


def test_save_returns_zero(sd, capsys):
    args = _Args(snapshot_cmd="save", name="p1", output="out", snapshot_dir=sd)
    assert handle_snapshot(args) == 0
    captured = capsys.readouterr()
    assert "p1" in captured.out


def test_show_after_save_returns_zero(sd, capsys):
    save_args = _Args(snapshot_cmd="save", name="p2", output="data", snapshot_dir=sd)
    handle_snapshot(save_args)
    show_args = _Args(snapshot_cmd="show", name="p2", snapshot_dir=sd)
    assert handle_snapshot(show_args) == 0
    captured = capsys.readouterr()
    assert "data" in captured.out


def test_diff_unchanged_returns_zero(sd):
    save_args = _Args(snapshot_cmd="save", name="p3", output="same", snapshot_dir=sd)
    handle_snapshot(save_args)
    diff_args = _Args(snapshot_cmd="diff", name="p3", output="same", snapshot_dir=sd)
    assert handle_snapshot(diff_args) == 0


def test_diff_changed_returns_one(sd):
    save_args = _Args(snapshot_cmd="save", name="p4", output="old", snapshot_dir=sd)
    handle_snapshot(save_args)
    diff_args = _Args(snapshot_cmd="diff", name="p4", output="new", snapshot_dir=sd)
    assert handle_snapshot(diff_args) == 1


def test_diff_no_snapshot_returns_one(sd):
    diff_args = _Args(snapshot_cmd="diff", name="ghost", output="x", snapshot_dir=sd)
    assert handle_snapshot(diff_args) == 1
