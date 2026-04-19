"""Integration tests: annotations subcommand wired into argument parser."""
import argparse
from pipewatch.cli_annotations import _add_subcommands, _DEFAULT_FILE


def _make_parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    _add_subcommands(sub)
    return p


def test_subcommand_registered():
    p = _make_parser()
    args = p.parse_args(["annotate", "add", "my_pipe", "some note"])
    assert args.command == "annotate"
    assert args.ann_cmd == "add"


def test_add_captures_pipeline_and_note():
    p = _make_parser()
    args = p.parse_args(["annotate", "add", "etl", "check logs"])
    assert args.pipeline == "etl"
    assert args.note == "check logs"


def test_add_default_author():
    p = _make_parser()
    args = p.parse_args(["annotate", "add", "etl", "note"])
    assert args.author == ""


def test_custom_file():
    p = _make_parser()
    args = p.parse_args(["annotate", "--file", "/tmp/ann.json", "show", "pipe"])
    assert args.file == "/tmp/ann.json"


def test_default_file():
    p = _make_parser()
    args = p.parse_args(["annotate", "show", "pipe"])
    assert args.file == _DEFAULT_FILE
