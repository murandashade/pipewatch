"""Aggregate runtime metrics from pipeline history."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from pipewatch.history import load_history


@dataclass
class PipelineMetrics:
    name: str
    total_runs: int = 0
    success_count: int = 0
    failure_count: int = 0
    avg_duration_s: Optional[float] = None
    max_duration_s: Optional[float] = None
    min_duration_s: Optional[float] = None
    durations: List[float] = field(default_factory=list, repr=False)

    @property
    def success_rate(self) -> Optional[float]:
        if self.total_runs == 0:
            return None
        return self.success_count / self.total_runs


def compute_metrics(history_path: str, pipeline_name: str) -> PipelineMetrics:
    records = load_history(history_path)
    m = PipelineMetrics(name=pipeline_name)
    for r in records:
        if r.get("pipeline") != pipeline_name:
            continue
        m.total_runs += 1
        if r.get("success"):
            m.success_count += 1
        else:
            m.failure_count += 1
        dur = r.get("duration_s")
        if dur is not None:
            m.durations.append(float(dur))
    if m.durations:
        m.avg_duration_s = sum(m.durations) / len(m.durations)
        m.max_duration_s = max(m.durations)
        m.min_duration_s = min(m.durations)
    return m


def format_metrics_text(m: PipelineMetrics) -> str:
    lines = [
        f"Pipeline : {m.name}",
        f"Runs     : {m.total_runs}",
        f"Successes: {m.success_count}",
        f"Failures : {m.failure_count}",
    ]
    if m.success_rate is not None:
        lines.append(f"Success% : {m.success_rate * 100:.1f}%")
    if m.avg_duration_s is not None:
        lines.append(f"Avg dur  : {m.avg_duration_s:.2f}s")
        lines.append(f"Min dur  : {m.min_duration_s:.2f}s")
        lines.append(f"Max dur  : {m.max_duration_s:.2f}s")
    return "\n".join(lines)
