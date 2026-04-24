"""Aggregate health scoring for pipelines based on recent run history."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from pipewatch.history import load_history
from pipewatch.baseline import get_baseline
from pipewatch.mute import is_muted


@dataclass
class HealthScore:
    pipeline: str
    score: int          # 0-100
    grade: str          # A/B/C/D/F
    total_runs: int
    recent_failures: int
    is_slow: bool
    is_muted: bool
    summary: str


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def compute_health(
    pipeline: str,
    history_file: str = ".pipewatch_history.json",
    baseline_file: str = ".pipewatch_baseline.json",
    mute_file: str = ".pipewatch_mute.json",
    window: int = 10,
) -> HealthScore:
    """Compute a health score for *pipeline* based on the last *window* runs."""
    entries = [
        e for e in load_history(history_file) if e.get("pipeline") == pipeline
    ]
    recent = entries[-window:]
    total = len(recent)
    failures = sum(1 for e in recent if not e.get("success", True))

    if total == 0:
        score = 50
    else:
        failure_rate = failures / total
        score = max(0, int(100 - failure_rate * 100))

    baseline = get_baseline(pipeline, baseline_file)
    slow = False
    if baseline is not None and recent:
        last_duration = recent[-1].get("duration_seconds")
        if last_duration is not None and last_duration > baseline * 1.5:
            slow = True
            score = max(0, score - 10)

    muted = is_muted(pipeline, mute_file)
    grade = _grade(score)
    summary = (
        f"{failures}/{total} recent failures; "
        f"{'slow; ' if slow else ''}"
        f"{'muted' if muted else 'active'}"
    )
    return HealthScore(
        pipeline=pipeline,
        score=score,
        grade=grade,
        total_runs=total,
        recent_failures=failures,
        is_slow=slow,
        is_muted=muted,
        summary=summary,
    )


def all_health_scores(
    pipelines: List[str],
    history_file: str = ".pipewatch_history.json",
    baseline_file: str = ".pipewatch_baseline.json",
    mute_file: str = ".pipewatch_mute.json",
    window: int = 10,
) -> List[HealthScore]:
    return [
        compute_health(p, history_file, baseline_file, mute_file, window)
        for p in pipelines
    ]


def format_health_text(scores: List[HealthScore]) -> str:
    if not scores:
        return "No pipeline health data available."
    lines = [f"{'Pipeline':<30} {'Grade':>5} {'Score':>6}  Summary"]
    lines.append("-" * 72)
    for s in scores:
        lines.append(f"{s.pipeline:<30} {s.grade:>5} {s.score:>6}  {s.summary}")
    return "\n".join(lines)
