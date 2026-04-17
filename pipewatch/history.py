"""Lightweight append-only run history stored as newline-delimited JSON."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def record_run(
    pipeline: str,
    success: bool,
    command: str,
    duration: float,
    path: str,
    timestamp: Optional[str] = None,
) -> None:
    """Append a run record to *path* (creates file if absent)."""
    entry: Dict[str, Any] = {
        "pipeline": pipeline,
        "success": success,
        "command": command,
        "duration_s": round(duration, 3),
        "timestamp": timestamp or _now_iso(),
    }
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def load_history(path: str) -> List[Dict[str, Any]]:
    """Return all records from *path*; empty list if file missing."""
    if not os.path.exists(path):
        return []
    records = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records


def last_failure(pipeline: str, path: str) -> Optional[Dict[str, Any]]:
    """Return the most recent failure record for *pipeline*, or None."""
    records = [
        r for r in load_history(path)
        if r.get("pipeline") == pipeline and not r.get("success", True)
    ]
    return records[-1] if records else None


def failure_streak(pipeline: str, path: str) -> int:
    """Return the current consecutive failure count for *pipeline*."""
    records = [
        r for r in load_history(path)
        if r.get("pipeline") == pipeline
    ]
    streak = 0
    for record in reversed(records):
        if not record.get("success", True):
            streak += 1
        else:
            break
    return streak
