import json
import pytest
from pathlib import Path
from pipewatch.cli_labels import handle_labels, _parse_filters


@pytest.fixture
def config_file(tmp_path):
    data = {
        "webhookUrl": "https://hooks.example.com/test",
        "pipelines": [
            {"name": "ingest", "command": "echo ingest", "labels": {"env": "prod", "team": "data"}},
            {"name": "transform", "command": "echo transform", "labels": {"env": "dev", "team": "data"}},
            {"name": "export", "command": "echo export", "labels": {"env": "prod", "team": "eng"}},
        ],
    }
    p = tmp_path / "pipewatch.json"
    p.write_text(json.dumps(data))
    return str(p)


class _Args:
    def __init__(self, config, filters=None, match_any=False, keys=False):
        self.config = config
        self.filters = filters
        self.match_any = match_any
        self.keys = keys


def test_returns_zero_on_success(config_file, capsys):
    assert handle_labels(_Args(config_file)) == 0


def test_missing_config_returns_two(tmp_path):
    assert handle_labels(_Args(str(tmp_path / "missing.json"))) == 2


def test_filter_by_single_label(config_file, capsys):
    rc = handle_labels(_Args(config_file, filters=["env=prod"]))
    assert rc == 0
    out = capsys.readouterr().out
    assert "ingest" in out
    assert "export" in out
    assert "transform" not in out


def test_filter_match_any(config_file, capsys):
    rc = handle_labels(_Args(config_file, filters=["env=prod", "team=data"], match_any=True))
    assert rc == 0
    out = capsys.readouterr().out
    assert "ingest" in out
    assert "transform" in out
    assert "export" in out


def test_keys_flag(config_file, capsys):
    rc = handle_labels(_Args(config_file, keys=True))
    assert rc == 0
    out = capsys.readouterr().out
    assert "env" in out
    assert "team" in out


def test_invalid_filter_returns_two(config_file):
    assert handle_labels(_Args(config_file, filters=["badfilter"])) == 2


def test_parse_filters_valid():
    assert _parse_filters(["env=prod", "team=data"]) == {"env": "prod", "team": "data"}


def test_parse_filters_invalid_raises():
    with pytest.raises(ValueError):
        _parse_filters(["noequals"])
