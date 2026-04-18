"""Tag-based filtering utilities for pipelines."""
from __future__ import annotations
from typing import List
from pipewatch.config import PipelineConfig


def pipelines_with_tag(pipelines: List[PipelineConfig], tag: str) -> List[PipelineConfig]:
    """Return pipelines that include *tag*."""
    return [p for p in pipelines if tag in (p.tags or [])]


def pipelines_matching_tags(
    pipelines: List[PipelineConfig],
    tags: List[str],
    match_all: bool = False,
) -> List[PipelineConfig]:
    """Filter pipelines by a list of tags.

    Args:
        pipelines: All configured pipelines.
        tags: Tags to filter by.
        match_all: If True every tag must be present; if False any tag suffices.
    """
    if not tags:
        return list(pipelines)
    if match_all:
        return [p for p in pipelines if all(t in (p.tags or []) for t in tags)]
    return [p for p in pipelines if any(t in (p.tags or []) for t in tags)]


def all_tags(pipelines: List[PipelineConfig]) -> List[str]:
    """Return a sorted, deduplicated list of every tag used across *pipelines*."""
    seen: set[str] = set()
    for p in pipelines:
        seen.update(p.tags or [])
    return sorted(seen)
