import argparse
import pytest
from pipewatch.cli_oncall import _add_subcommands, _DEFAULT_FILE


def _make_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    _add_subcommands(sub)
    return parser


def test_subcommand_registered():
    parser = _make_parser()
    args = parser.parse_args(["oncall", "list"])
    assert args.command == "oncall"
    assert args.oncall_cmd == "list"


def test_set_captures_pipeline_and_contact():
    parser = _make_parser()
    args = parser.parse_args(["oncall", "set", "my-pipeline", "ops@example.com"])
    assert args.pipeline == "my-pipeline"
    assert args.contact == "ops@example.com"


def test_default_file():
    parser = _make_parser()
    args = parser.parse_args(["oncall", "list"])
    assert args.file == _DEFAULT_FILE


def test_custom_file():
    parser = _make_parser()
    args = parser.parse_args(["oncall", "list", "--file", "/tmp/oc.json"])
    assert args.file == "/tmp/oc.json"


def test_show_requires_pipeline():
    parser = _make_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["oncall", "show"])
