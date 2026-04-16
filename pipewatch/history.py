"""Persist and query pipeline run history to a local JSON file."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import List, Optional

DEFAULT_HISTORY_FILE = ".pipewatch_history.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_run(
    name: str,
    success: bool,
    exit_code: int,
    duration: float,
    history_file: str = DEFAULT_HISTORY_FILE,
) -> dict:
    """Append a run record to the history file and return the record."""
    record = {
        "pipeline": name,
        "success": success,
        "exit_code": exit_code,
        "duration_seconds": round(duration, 3),
        "timestamp": _now_iso(),
    }
    entries = load_history(history_file)
    entries.append(record)
    with open(history_file, "w") as fh:
        json.dump(entries, fh, indent=2)
    return record


def load_history(history_file: str = DEFAULT_HISTORY_FILE) -> List[dict]:
    """Return all history entries, or an empty list if the file is absent."""
    if not os.path.exists(history_file):
        return []
    with open(history_file) as fh:
        return json.load(fh)


def last_failure(name: str, history_file: str = DEFAULT_HISTORY_FILE) -> Optional[dict]:
    """Return the most recent failed run for *name*, or None."""
    entries = load_history(history_file)
    for entry in reversed(entries):
        if entry["pipeline"] == name and not entry["success"]:
            return entry
    return None


def failure_streak(name: str, history_file: str = DEFAULT_HISTORY_FILE) -> int:
    """Return how many consecutive failures *name* has at the tail of history."""
    entries = [e for e in load_history(history_file) if e["pipeline"] == name]
    streak = 0
    for entry in reversed(entries):
        if not entry["success"]:
            streak += 1
        else:
            break
    return streak
