"""Pipeline label management — attach arbitrary key=value labels and filter by them."""
from __future__ import annotations
from typing import Dict, List
from pipewatch.config import PipelineConfig


def pipelines_with_label(pipelines: List[PipelineConfig], key: str, value: str) -> List[PipelineConfig]:
    """Return pipelines where labels[key] == value."""
    return [p for p in pipelines if p.labels.get(key) == value]


def pipelines_matching_labels(pipelines: List[PipelineConfig], labels: Dict[str, str], match_all: bool = True) -> List[PipelineConfig]:
    """Return pipelines matching all (or any) of the given key=value label pairs."""
    def _matches(p: PipelineConfig) -> bool:
        pairs = [(p.labels.get(k) == v) for k, v in labels.items()]
        return all(pairs) if match_all else any(pairs)
    return [p for p in pipelines if _matches(p)]


def all_label_keys(pipelines: List[PipelineConfig]) -> List[str]:
    """Return sorted unique label keys across all pipelines."""
    keys: set = set()
    for p in pipelines:
        keys.update(p.labels.keys())
    return sorted(keys)


def format_labels_text(pipelines: List[PipelineConfig]) -> str:
    """Render a human-readable table of pipeline labels."""
    if not pipelines:
        return "No pipelines found."
    lines = []
    for p in pipelines:
        label_str = ", ".join(f"{k}={v}" for k, v in sorted(p.labels.items())) or "(none)"
        lines.append(f"  {p.name}: {label_str}")
    return "\n".join(lines)
