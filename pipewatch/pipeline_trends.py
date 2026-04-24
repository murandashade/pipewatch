"""Compute run-over-run trend data for pipelines."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

from pipewatch.history import load_history


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class TrendPoint:
    timestamp: str
    success: bool
    duration_seconds: float


@dataclass
class PipelineTrend:
    pipeline: str
    points: List[TrendPoint]
    avg_duration: float
    success_rate: float
    direction: str  # "improving", "degrading", "stable"


def _parse_dt(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def compute_trend(
    pipeline: str,
    history_file: str,
    window: int = 20,
    since: Optional[str] = None,
) -> PipelineTrend:
    """Build a PipelineTrend for *pipeline* using the last *window* runs."""
    entries = load_history(history_file)
    filtered = [e for e in entries if e.get("pipeline") == pipeline]

    if since:
        since_dt = _parse_dt(since)
        filtered = [e for e in filtered if _parse_dt(e["timestamp"]) >= since_dt]

    filtered = filtered[-window:]

    points = [
        TrendPoint(
            timestamp=e["timestamp"],
            success=e.get("success", False),
            duration_seconds=float(e.get("duration_seconds", 0.0)),
        )
        for e in filtered
    ]

    if not points:
        return PipelineTrend(
            pipeline=pipeline, points=[], avg_duration=0.0,
            success_rate=0.0, direction="stable"
        )

    avg_duration = sum(p.duration_seconds for p in points) / len(points)
    success_rate = sum(1 for p in points if p.success) / len(points)

    direction = _compute_direction(points)

    return PipelineTrend(
        pipeline=pipeline,
        points=points,
        avg_duration=round(avg_duration, 3),
        success_rate=round(success_rate, 4),
        direction=direction,
    )


def _compute_direction(points: List[TrendPoint]) -> str:
    """Compare first-half vs second-half success rates to determine trend."""
    if len(points) < 4:
        return "stable"
    mid = len(points) // 2
    first_half = points[:mid]
    second_half = points[mid:]
    first_rate = sum(1 for p in first_half if p.success) / len(first_half)
    second_rate = sum(1 for p in second_half if p.success) / len(second_half)
    delta = second_rate - first_rate
    if delta > 0.1:
        return "improving"
    if delta < -0.1:
        return "degrading"
    return "stable"


def format_trend_text(trend: PipelineTrend) -> str:
    lines = [
        f"Pipeline : {trend.pipeline}",
        f"Runs     : {len(trend.points)}",
        f"Avg dur  : {trend.avg_duration}s",
        f"Success% : {trend.success_rate * 100:.1f}%",
        f"Trend    : {trend.direction}",
    ]
    return "\n".join(lines)
