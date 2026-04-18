"""Simple cron-style schedule checker for pipelines."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional


_CRON_RE = re.compile(
    r'^(\*|\d+)\s+(\*|\d+)\s+(\*|\d+)\s+(\*|\d+)\s+(\*|\d+)$'
)


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def parse_cron(expr: str) -> tuple[str, str, str, str, str]:
    """Parse a 5-field cron expression; raise ValueError on bad input."""
    m = _CRON_RE.match(expr.strip())
    if not m:
        raise ValueError(f"Invalid cron expression: {expr!r}")
    return m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)


def _field_matches(field: str, value: int) -> bool:
    if field == '*':
        return True
    return int(field) == value


def is_due(expr: str, at: Optional[datetime] = None) -> bool:
    """Return True if *expr* matches the given datetime (default: now UTC)."""
    minute, hour, dom, month, dow = parse_cron(expr)
    dt = at or _utcnow()
    return (
        _field_matches(minute, dt.minute)
        and _field_matches(hour, dt.hour)
        and _field_matches(dom, dt.day)
        and _field_matches(month, dt.month)
        and _field_matches(dow, dt.weekday())
    )


def due_pipelines(config, at: Optional[datetime] = None) -> list:
    """Return pipelines from *config* whose schedule is due at *at*."""
    due = []
    for pipeline in config.pipelines:
        schedule: Optional[str] = getattr(pipeline, 'schedule', None)
        if schedule and is_due(schedule, at=at):
            due.append(pipeline)
    return due
