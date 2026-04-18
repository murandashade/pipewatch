"""Integration: metrics subcommand registration."""
import argparse

from pipewatch.cli_metrics import _add_subcommands


def test_subcommand_registered():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    _add_subcommands(sub)
    args = parser.parse_args(["metrics", "my_pipeline"])
    assert args.pipeline == "my_pipeline"
    assert args.func is not None


def test_json_flag_default_false():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    _add_subcommands(sub)
    args = parser.parse_args(["metrics", "etl"])
    assert args.json is False


def test_json_flag_true():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    _add_subcommands(sub)
    args = parser.parse_args(["metrics", "etl", "--json"])
    assert args.json is True


def test_custom_history_file():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    _add_subcommands(sub)
    args = parser.parse_args(["metrics", "etl", "--history", "custom.jsonl"])
    assert args.history == "custom.jsonl"
