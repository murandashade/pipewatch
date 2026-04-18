"""Tests for pipewatch.cli_export."""
import json
import argparse
import pytest
from pathlib import Path

from pipewatch.cli_export import handle_export, _add_subcommands


@pytest.fixture()
def hist_file(tmp_path: Path) -> Path:
    p = tmp_path / "history.jsonl"
    records = [
        {"pipeline": "ingest", "timestamp": "2024-01-01T00:00:00Z", "success": True, "exit_code": 0, "duration_s": 1.0},
    ]
    with p.open("w") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")
    return p


def _args(**kwargs):
    defaults = {"fmt": "json", "pipeline": None, "output": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_returns_zero_on_success(hist_file, capsys):
    rc = handle_export(_args(history_file=str(hist_file)))
    assert rc == 0


def test_json_output_to_stdout(hist_file, capsys):
    handle_export(_args(history_file=str(hist_file)))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, list)
    assert data[0]["pipeline"] == "ingest"


def test_csv_output_to_stdout(hist_file, capsys):
    handle_export(_args(history_file=str(hist_file), fmt="csv"))
    out = capsys.readouterr().out
    assert "pipeline,timestamp" in out


def test_missing_history_returns_two(tmp_path):
    rc = handle_export(_args(history_file=str(tmp_path / "missing.jsonl")))
    assert rc == 2


def test_output_to_file(hist_file, tmp_path):
    out_file = tmp_path / "out.json"
    rc = handle_export(_args(history_file=str(hist_file), output=str(out_file)))
    assert rc == 0
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert len(data) == 1


def test_subcommand_registered():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    _add_subcommands(sub)
    args = parser.parse_args(["export", "--format", "csv"])
    assert args.fmt == "csv"
