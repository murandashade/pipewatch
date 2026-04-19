"""Per-pipeline alert throttling based on time windows."""
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

_STATE_FILE = ".pipewatch_throttle.json"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save(path: Path, state: dict) -> None:
    path.write_text(json.dumps(state, indent=2))


def is_throttled(pipeline_name: str, window_seconds: int, state_dir: str = ".") -> bool:
    """Return True if an alert for *pipeline_name* was sent within *window_seconds*."""
    path = Path(state_dir) / _STATE_FILE
    state = _load(path)
    last_str: Optional[str] = state.get(pipeline_name)
    if last_str is None:
        return False
    last = datetime.fromisoformat(last_str)
    return (_utcnow() - last) < timedelta(seconds=window_seconds)


def record_alert(pipeline_name: str, state_dir: str = ".") -> None:
    """Record that an alert was just sent for *pipeline_name*."""
    path = Path(state_dir) / _STATE_FILE
    state = _load(path)
    state[pipeline_name] = _utcnow().isoformat()
    _save(path, state)


def clear_throttle(pipeline_name: str, state_dir: str = ".") -> None:
    """Remove throttle state for *pipeline_name*."""
    path = Path(state_dir) / _STATE_FILE
    state = _load(path)
    state.pop(pipeline_name, None)
    _save(path, state)
