"""Cron-style schedule helpers for pipewatch."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Sequence

from pipewatch.config import PipelineConfig


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def parse_cron(expr: str) -> tuple[str, str, str, str, str]:
    """Parse a 5-field cron expression and return the fields."""
    fields = expr.strip().split()
    if len(fields) != 5:
        raise ValueError(f"Expected 5 cron fields, got {len(fields)}: {expr!r}")
    for f in fields:
        if not all(c.isdigit() or c in "*,-/" for c in f):
            raise ValueError(f"Invalid cron field: {f!r}")
    return tuple(fields)  # type: ignore[return-value]


def _field_matches(field: str, value: int) -> bool:
    if field == "*":
        return True
    for part in field.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            start = 0 if base == "*" else int(base)
            if (value - start) % int(step) == 0 and value >= start:
                return True
        elif "-" in part:
            lo, hi = part.split("-", 1)
            if int(lo) <= value <= int(hi):
                return True
        else:
            if int(part) == value:
                return True
    return False


def is_due(expr: str, at: datetime | None = None) -> bool:
    """Return True if *expr* matches the given datetime (default: now)."""
    if at is None:
        at = _utcnow()
    minute, hour, dom, month, dow = parse_cron(expr)
    return (
        _field_matches(minute, at.minute)
        and _field_matches(hour, at.hour)
        and _field_matches(dom, at.day)
        and _field_matches(month, at.month)
        and _field_matches(dow, at.weekday())
    )


def due_pipelines(
    pipelines: Sequence[PipelineConfig], at: datetime | None = None
) -> List[PipelineConfig]:
    """Return pipelines whose schedule is due at *at*."""
    if at is None:
        at = _utcnow()
    result = []
    for pl in pipelines:
        if pl.schedule and is_due(pl.schedule, at):
            result.append(pl)
    return result
