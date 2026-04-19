import argparse
from pipewatch.cli_runbook import _add_subcommands


def _make_parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    _add_subcommands(sub)
    return p


def test_subcommand_registered():
    p = _make_parser()
    args = p.parse_args(["runbook", "list"])
    assert args.command == "runbook"


def test_add_captures_url():
    p = _make_parser()
    args = p.parse_args(["runbook", "add", "etl", "https://wiki"])
    assert args.url == "https://wiki"
    assert args.pipeline == "etl"


def test_add_note_default_empty():
    p = _make_parser()
    args = p.parse_args(["runbook", "add", "etl", "https://wiki"])
    assert args.note == ""


def test_add_custom_note():
    p = _make_parser()
    args = p.parse_args(["runbook", "add", "etl", "https://wiki", "--note", "see docs"])
    assert args.note == "see docs"


def test_default_file():
    from pipewatch.runbook import _DEFAULT_FILE
    p = _make_parser()
    args = p.parse_args(["runbook", "list"])
    assert args.file == _DEFAULT_FILE
