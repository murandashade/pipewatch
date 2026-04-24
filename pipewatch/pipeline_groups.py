"""Pipeline grouping — organise pipelines into named groups."""
from __future__ import annotations

from typing import Dict, List

from pipewatch.config import PipelineConfig


def pipelines_in_group(
    pipelines: List[PipelineConfig], group: str
) -> List[PipelineConfig]:
    """Return pipelines whose 'group' field matches *group* (case-insensitive)."""
    target = group.strip().lower()
    return [p for p in pipelines if (p.group or "").strip().lower() == target]


def all_groups(pipelines: List[PipelineConfig]) -> List[str]:
    """Return a sorted, deduplicated list of all group names."""
    seen: set[str] = set()
    result: List[str] = []
    for p in pipelines:
        g = (p.group or "").strip()
        if g and g not in seen:
            seen.add(g)
            result.append(g)
    return sorted(result)


def group_map(pipelines: List[PipelineConfig]) -> Dict[str, List[PipelineConfig]]:
    """Return a dict mapping each group name to its member pipelines."""
    mapping: Dict[str, List[PipelineConfig]] = {}
    for p in pipelines:
        g = (p.group or "").strip()
        if g:
            mapping.setdefault(g, []).append(p)
    return mapping


def format_groups_text(mapping: Dict[str, List[PipelineConfig]]) -> str:
    """Render a human-readable summary of groups and their pipelines."""
    if not mapping:
        return "No groups defined."
    lines: List[str] = []
    for group in sorted(mapping):
        members = ", ".join(p.name for p in mapping[group])
        lines.append(f"{group}: {members}")
    return "\n".join(lines)
