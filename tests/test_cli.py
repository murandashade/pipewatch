"""Tests for the pipewatch CLI entry point."""
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from pipewatch.cli import main
from pipewatch.monitor import RunResult


@pytest.fixture()
def config_file(tmp_path: Path) -> Path:
    cfg = {
        "webhook_url": "https://hooks.example.com/default",
        "pipelines": [
            {"name": "etl-daily", "command": "echo ok"}
        ],
    }
    p = tmp_path / "pipewatch.json"
    p.write_text(json.dumps(cfg))
    return p


def _ok_result(name: str = "etl-daily") -> RunResult:
    return RunResult(pipeline=name, success=True, returncode=0, stdout="ok", stderr="", duration=0.1)


def _fail_result(name: str = "etl-daily") -> RunResult:
    return RunResult(pipeline=name, success=False, returncode=1, stdout="", stderr="err", duration=0.1)


def test_dry_run_exits_zero(config_file: Path):
    code = main(["-c", str(config_file), "--dry-run"])
    assert code == 0


def test_missing_config_exits_two():
    code = main(["-c", "nonexistent.json"])
    assert code == 2


def test_all_pass_exits_zero(config_file: Path):
    with patch("pipewatch.cli.run_all", return_value=[_ok_result()]):
        code = main(["-c", str(config_file)])
    assert code == 0


def test_any_failure_exits_one(config_file: Path):
    with patch("pipewatch.cli.run_all", return_value=[_fail_result()]):
        code = main(["-c", str(config_file)])
    assert code == 1


def test_quiet_suppresses_output(config_file: Path, capsys):
    with patch("pipewatch.cli.run_all", return_value=[_ok_result()]):
        main(["-c", str(config_file), "--quiet"])
    captured = capsys.readouterr()
    assert captured.out == ""


def test_invalid_config_exits_two(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"pipelines": []}))
    code = main(["-c", str(bad)])
    assert code == 2
