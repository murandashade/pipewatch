"""Compare pipeline metrics across two time windows."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from pipewatch.metrics import compute_metrics, PipelineMetrics
from pipewatch.history import load_history


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class CompareResult:
    pipeline: str
    window_a_runs: int
    window_b_runs: int
    window_a_success_rate: float
    window_b_success_rate: float
    window_a_avg_duration: Optional[float]
    window_b_avg_duration: Optional[float]

    @property
    def success_rate_delta(self) -> float:
        return self.window_b_success_rate - self.window_a_success_rate

    @property
    def duration_delta(self) -> Optional[float]:
        if self.window_a_avg_duration is None or self.window_b_avg_duration is None:
            return None
        return self.window_b_avg_duration - self.window_a_avg_duration


def compare_pipeline(
    name: str,
    history_file: str,
    since_a: datetime,
    until_a: datetime,
    since_b: datetime,
    until_b: datetime,
) -> CompareResult:
    """Compare metrics for *name* between two time windows."""
    m_a: PipelineMetrics = compute_metrics(name, history_file, since=since_a, until=until_a)
    m_b: PipelineMetrics = compute_metrics(name, history_file, since=since_b, until=until_b)
    return CompareResult(
        pipeline=name,
        window_a_runs=m_a.total_runs,
        window_b_runs=m_b.total_runs,
        window_a_success_rate=m_a.success_rate,
        window_b_success_rate=m_b.success_rate,
        window_a_avg_duration=m_a.avg_duration_seconds,
        window_b_avg_duration=m_b.avg_duration_seconds,
    )


def format_compare_text(result: CompareResult) -> str:
    """Return a human-readable comparison summary."""
    lines = [
        f"Pipeline : {result.pipeline}",
        f"Runs     : {result.window_a_runs} → {result.window_b_runs}",
        f"Success% : {result.window_a_success_rate:.1f}% → {result.window_b_success_rate:.1f}%"
        f"  (delta {result.success_rate_delta:+.1f}%)",
    ]
    if result.duration_delta is not None:
        lines.append(
            f"Avg dur  : {result.window_a_avg_duration:.2f}s → {result.window_b_avg_duration:.2f}s"
            f"  (delta {result.duration_delta:+.2f}s)"
        )
    else:
        lines.append("Avg dur  : n/a")
    return "\n".join(lines)
