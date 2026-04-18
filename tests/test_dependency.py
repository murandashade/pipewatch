"""Tests for pipewatch.dependency."""
import pytest
from unittest.mock import MagicMock
from pipewatch.dependency import build_graph, topological_sort, execution_order, CycleError


def _p(name, depends_on=None):
    m = MagicMock()
    m.name = name
    m.depends_on = depends_on or []
    return m


def test_build_graph_no_deps():
    pipelines = [_p("a"), _p("b")]
    g = build_graph(pipelines)
    assert g == {"a": [], "b": []}


def test_build_graph_with_deps():
    pipelines = [_p("a"), _p("b", ["a"])]
    g = build_graph(pipelines)
    assert g["b"] == ["a"]


def test_build_graph_unknown_dep_raises():
    pipelines = [_p("a", ["missing"])]
    with pytest.raises(ValueError, match="unknown dependencies"):
        build_graph(pipelines)


def test_topological_sort_simple():
    graph = {"a": [], "b": ["a"], "c": ["b"]}
    order = topological_sort(graph)
    assert order.index("a") < order.index("b") < order.index("c")


def test_topological_sort_no_deps():
    graph = {"x": [], "y": [], "z": []}
    order = topological_sort(graph)
    assert set(order) == {"x", "y", "z"}


def test_topological_sort_cycle_raises():
    graph = {"a": ["b"], "b": ["a"]}
    with pytest.raises(CycleError):
        topological_sort(graph)


def test_execution_order_respects_deps():
    pipelines = [_p("load", ["extract"]), _p("extract"), _p("transform", ["extract"])]
    ordered = execution_order(pipelines)
    names = [p.name for p in ordered]
    assert names.index("extract") < names.index("load")
    assert names.index("extract") < names.index("transform")


def test_execution_order_no_deps_returns_all():
    pipelines = [_p("a"), _p("b"), _p("c")]
    ordered = execution_order(pipelines)
    assert {p.name for p in ordered} == {"a", "b", "c"}
