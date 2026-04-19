import argparse
from pipewatch.cli_snapshots import _add_subcommands


def _make_parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    _add_subcommands(sub)
    return p


def test_subcommand_registered():
    p = _make_parser()
    args = p.parse_args(["snapshot", "show", "mypipe"])
    assert args.snapshot_cmd == "show"
    assert args.name == "mypipe"


def test_save_subcommand_args():
    p = _make_parser()
    args = p.parse_args(["snapshot", "save", "pipe1", "some output"])
    assert args.snapshot_cmd == "save"
    assert args.output == "some output"


def test_diff_subcommand_args():
    p = _make_parser()
    args = p.parse_args(["snapshot", "diff", "pipe2", "current"])
    assert args.snapshot_cmd == "diff"
    assert args.name == "pipe2"
    assert args.output == "current"


def test_default_snapshot_dir():
    p = _make_parser()
    args = p.parse_args(["snapshot", "show", "x"])
    assert args.snapshot_dir == ".pipewatch/snapshots"


def test_custom_snapshot_dir():
    p = _make_parser()
    args = p.parse_args(["snapshot", "show", "x", "--snapshot-dir", "/tmp/s"])
    assert args.snapshot_dir == "/tmp/s"
