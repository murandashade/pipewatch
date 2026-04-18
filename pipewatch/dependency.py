"""Pipeline dependency ordering and cycle detection."""
from __future__ import annotations
from typing import Dict, List, Optional
from pipewatch.config import PipelineConfig


class CycleError(Exception):
    """Raised when a dependency cycle is detected."""


def build_graph(pipelines: List[PipelineConfig]) -> Dict[str, List[str]]:
    """Return adjacency list: name -> list of dependency names."""
    names = {p.name for p in pipelines}
    graph: Dict[str, List[str]] = {}
    for p in pipelines:
        deps = getattr(p, "depends_on", None) or []
        unknown = [d for d in deps if d not in names]
        if unknown:
            raise ValueError(f"Pipeline '{p.name}' has unknown dependencies: {unknown}")
        graph[p.name] = list(deps)
    return graph


def topological_sort(graph: Dict[str, List[str]]) -> List[str]:
    """Return pipeline names in dependency-safe execution order."""
    visited: set = set()
    temp: set = set()
    order: List[str] = []

    def visit(node: str) -> None:
        if node in temp:
            raise CycleError(f"Cycle detected involving '{node}'")
        if node in visited:
            return
        temp.add(node)
        for dep in graph.get(node, []):
            visit(dep)
        temp.discard(node)
        visited.add(node)
        order.append(node)

    for name in graph:
        visit(name)
    return order


def execution_order(pipelines: List[PipelineConfig]) -> List[PipelineConfig]:
    """Return pipelines sorted so dependencies run before dependents."""
    graph = build_graph(pipelines)
    ordered_names = topological_sort(graph)
    by_name = {p.name: p for p in pipelines}
    return [by_name[n] for n in ordered_names]
