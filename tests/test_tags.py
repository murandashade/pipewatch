"""Tests for pipewatch.tags and pipewatch.cli_tags."""
from __future__ import annotations
import json
import pytest
from unittest.mock import patch
from pipewatch.config import PipelineConfig
from pipewatch import tags as tags_mod


def _make(name: str, t: list[str] | None = None) -> PipelineConfig:
    return PipelineConfig(name=name, command=f"echo {name}", tags=t)


ALL = [
    _make("a", ["etl", "critical"]),
    _make("b", ["etl"]),
    _make("c", ["reporting"]),
    _make("d"),
]


def test_pipelines_with_tag():
    result = tags_mod.pipelines_with_tag(ALL, "etl")
    assert [p.name for p in result] == ["a", "b"]


def test_pipelines_with_tag_no_match():
    assert tags_mod.pipelines_with_tag(ALL, "missing") == []


def test_pipelines_matching_tags_any():
    result = tags_mod.pipelines_matching_tags(ALL, ["etl", "reporting"])
    assert {p.name for p in result} == {"a", "b", "c"}


def test_pipelines_matching_tags_all():
    result = tags_mod.pipelines_matching_tags(ALL, ["etl", "critical"], match_all=True)
    assert [p.name for p in result] == ["a"]


def test_pipelines_matching_tags_empty_filter_returns_all():
    assert tags_mod.pipelines_matching_tags(ALL, []) == ALL


def test_all_tags():
    assert tags_mod.all_tags(ALL) == ["critical", "etl", "reporting"]


def test_all_tags_empty():
    assert tags_mod.all_tags([]) == []


# --- CLI integration ---


@pytest.fixture()
def config_file(tmp_path):
    data = {
        "pipelines": [
            {"name": "pipe-a", "command": "echo a", "tags": ["etl"]},
            {"name": "pipe-b", "command": "echo b", "tags": ["reporting"]},
        ]
    }
    p = tmp_path / "pipewatch.json"
    p.write_text(json.dumps(data))
    return str(p)


def _run(args):
    from pipewatch.cli_tags import handle_tags
    import argparse
    ns = argparse.Namespace(**args)
    return handle_tags(ns)


def test_list_tags(config_file, capsys):
    rc = _run({"config": config_file, "tags_cmd": "list"})
    assert rc == 0
    out = capsys.readouterr().out
    assert "etl" in out
    assert "reporting" in out


def test_filter_tags_match(config_file, capsys):
    rc = _run({"config": config_file, "tags_cmd": "filter", "tags": ["etl"], "match_all": False})
    assert rc == 0
    assert "pipe-a" in capsys.readouterr().out


def test_filter_tags_no_match(config_file, capsys):
    rc = _run({"config": config_file, "tags_cmd": "filter", "tags": ["missing"], "match_all": False})
    assert rc == 1


def test_missing_config(tmp_path):
    rc = _run({"config": str(tmp_path / "nope.json"), "tags_cmd": "list"})
    assert rc == 2
