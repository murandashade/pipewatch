"""Alert suppression policy: skip alerts when failure streak is below threshold
or when the pipeline is in a cooldown window."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional

from pipewatch.history import failure_streak, last_failure


@dataclass
class AlertPolicy:
    """Controls when an alert should actually be sent."""
    min_streak: int = 1          # alert only after this many consecutive failures
    cooldown_minutes: int = 0    # suppress repeated alerts within this window


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def should_alert(
    pipeline_name: str,
    history_path: str,
    policy: AlertPolicy,
) -> bool:
    """Return True if an alert should be fired for *pipeline_name*."""
    streak = failure_streak(pipeline_name, history_path)
    if streak < policy.min_streak:
        return False

    if policy.cooldown_minutes > 0:
        last = last_failure(pipeline_name, history_path)
        if last is not None:
            # last_failure returns the *previous* failure; if the streak just
            # reached min_streak the most recent entry IS the trigger, so we
            # look at the second-to-last implicitly via cooldown on last entry.
            try:
                ts = datetime.fromisoformat(last["timestamp"])
            except (KeyError, ValueError):
                return True
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            age = _utcnow() - ts
            if age < timedelta(minutes=policy.cooldown_minutes):
                return False

    return True
