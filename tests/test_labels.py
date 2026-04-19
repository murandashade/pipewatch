import pytest
from pipewatch.labels import (
    pipelines_with_label,
    pipelines_matching_labels,
    all_label_keys,
    format_labels_text,
)


class _P:
    def __init__(self, name, labels=None):
        self.name = name
        self.labels = labels or {}


def _make(name, **labels):
    return _P(name, labels)


def test_pipelines_with_label_match():
    ps = [_make("a", env="prod"), _make("b", env="dev"), _make("c", env="prod")]
    result = pipelines_with_label(ps, "env", "prod")
    assert [p.name for p in result] == ["a", "c"]


def test_pipelines_with_label_no_match():
    ps = [_make("a", env="dev")]
    assert pipelines_with_label(ps, "env", "prod") == []


def test_pipelines_with_label_missing_key():
    ps = [_make("a")]
    assert pipelines_with_label(ps, "env", "prod") == []


def test_pipelines_matching_labels_all():
    ps = [_make("a", env="prod", team="data"), _make("b", env="prod", team="eng"), _make("c", env="dev", team="data")]
    result = pipelines_matching_labels(ps, {"env": "prod", "team": "data"}, match_all=True)
    assert [p.name for p in result] == ["a"]


def test_pipelines_matching_labels_any():
    ps = [_make("a", env="prod"), _make("b", team="data"), _make("c")]
    result = pipelines_matching_labels(ps, {"env": "prod", "team": "data"}, match_all=False)
    assert [p.name for p in result] == ["a", "b"]


def test_all_label_keys_unique_sorted():
    ps = [_make("a", env="prod", team="data"), _make("b", env="dev", owner="alice")]
    assert all_label_keys(ps) == ["env", "owner", "team"]


def test_all_label_keys_empty():
    assert all_label_keys([]) == []


def test_format_labels_text_no_pipelines():
    assert format_labels_text([]) == "No pipelines found."


def test_format_labels_text_renders_labels():
    ps = [_make("etl", env="prod", team="data")]
    out = format_labels_text(ps)
    assert "etl" in out
    assert "env=prod" in out
    assert "team=data" in out


def test_format_labels_text_no_labels_shows_none():
    ps = [_make("etl")]
    assert "(none)" in format_labels_text(ps)
