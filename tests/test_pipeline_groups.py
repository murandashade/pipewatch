"""Tests for pipewatch.pipeline_groups."""
from __future__ import annotations

import pytest

from pipewatch.pipeline_groups import (
    all_groups,
    format_groups_text,
    group_map,
    pipelines_in_group,
)


class _P:
    """Minimal pipeline stand-in."""

    def __init__(self, name: str, group: str | None = None):
        self.name = name
        self.group = group


def _make(*specs: tuple[str, str | None]):
    return [_P(name, grp) for name, grp in specs]


def test_pipelines_in_group_match():
    pipelines = _make(("a", "etl"), ("b", "etl"), ("c", "reporting"))
    result = pipelines_in_group(pipelines, "etl")
    assert [p.name for p in result] == ["a", "b"]


def test_pipelines_in_group_case_insensitive():
    pipelines = _make(("a", "ETL"), ("b", "etl"))
    result = pipelines_in_group(pipelines, "ETL")
    assert len(result) == 2


def test_pipelines_in_group_no_match():
    pipelines = _make(("a", "etl"),)
    assert pipelines_in_group(pipelines, "reporting") == []


def test_pipelines_in_group_none_group():
    pipelines = _make(("a", None), ("b", "etl"))
    assert [p.name for p in pipelines_in_group(pipelines, "etl")] == ["b"]


def test_all_groups_sorted_deduped():
    pipelines = _make(("a", "etl"), ("b", "reporting"), ("c", "etl"), ("d", None))
    assert all_groups(pipelines) == ["etl", "reporting"]


def test_all_groups_empty():
    assert all_groups([]) == []


def test_group_map_structure():
    pipelines = _make(("a", "etl"), ("b", "etl"), ("c", "reporting"))
    mapping = group_map(pipelines)
    assert set(mapping.keys()) == {"etl", "reporting"}
    assert [p.name for p in mapping["etl"]] == ["a", "b"]


def test_group_map_excludes_ungrouped():
    pipelines = _make(("a", None), ("b", ""))
    assert group_map(pipelines) == {}


def test_format_groups_text_output():
    pipelines = _make(("a", "etl"), ("b", "etl"), ("c", "reporting"))
    text = format_groups_text(group_map(pipelines))
    assert "etl: a, b" in text
    assert "reporting: c" in text


def test_format_groups_text_empty():
    assert format_groups_text({}) == "No groups defined."
