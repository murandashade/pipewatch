"""Aggregate live status summary for all configured pipelines."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from pipewatch.history import load_history, last_failure, failure_streak
from pipewatch.mute import is_muted
from pipewatch.baseline import get_baseline


@dataclass
class PipelineStatus:
    name: str
    last_run: Optional[str] = None
    last_outcome: Optional[str] = None  # "success" | "failure" | None
    failure_streak: int = 0
    muted: bool = False
    baseline_seconds: Optional[float] = None
    last_duration: Optional[float] = None


def _last_entry(entries: list) -> Optional[dict]:
    return entries[-1] if entries else None


def pipeline_status(
    name: str,
    history_file: Path,
    mute_file: Path,
    baseline_file: Path,
) -> PipelineStatus:
    """Build a PipelineStatus for a single pipeline."""
    entries = [
        e for e in load_history(history_file) if e.get("pipeline") == name
    ]
    latest = _last_entry(entries)
    streak = failure_streak(name, history_file)
    muted = is_muted(name, mute_file)
    baseline = get_baseline(name, baseline_file)

    return PipelineStatus(
        name=name,
        last_run=latest.get("timestamp") if latest else None,
        last_outcome=latest.get("outcome") if latest else None,
        failure_streak=streak,
        muted=muted,
        baseline_seconds=baseline,
        last_duration=latest.get("duration") if latest else None,
    )


def all_pipeline_statuses(
    names: List[str],
    history_file: Path,
    mute_file: Path,
    baseline_file: Path,
) -> List[PipelineStatus]:
    """Return status for every pipeline in *names*."""
    return [
        pipeline_status(n, history_file, mute_file, baseline_file)
        for n in names
    ]


def format_status_text(statuses: List[PipelineStatus]) -> str:
    """Human-readable status table."""
    if not statuses:
        return "No pipelines configured."
    lines = [f"{'PIPELINE':<30} {'LAST RUN':<26} {'OUTCOME':<10} {'STREAK':>6} {'MUTED':>6}"]
    lines.append("-" * 82)
    for s in statuses:
        outcome = s.last_outcome or "never"
        last = s.last_run or "—"
        muted = "yes" if s.muted else "no"
        lines.append(f"{s.name:<30} {last:<26} {outcome:<10} {s.failure_streak:>6} {muted:>6}")
    return "\n".join(lines)
