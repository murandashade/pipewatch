"""Mute/silence alerts for specific pipelines for a given duration."""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

_DEFAULT_STATE = Path(".pipewatch") / "mute_state.json"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2))


def mute_pipeline(name: str, hours: float, path: Path = _DEFAULT_STATE) -> None:
    """Mute alerts for *name* for the given number of hours."""
    state = _load(path)
    until = (_utcnow() + timedelta(hours=hours)).isoformat()
    state[name] = {"muted_until": until}
    _save(path, state)


def unmute_pipeline(name: str, path: Path = _DEFAULT_STATE) -> bool:
    """Remove mute for *name*. Returns True if an entry was removed."""
    state = _load(path)
    if name in state:
        del state[name]
        _save(path, state)
        return True
    return False


def is_muted(name: str, path: Path = _DEFAULT_STATE) -> bool:
    """Return True if *name* is currently muted."""
    state = _load(path)
    entry = state.get(name)
    if entry is None:
        return False
    until = datetime.fromisoformat(entry["muted_until"])
    return _utcnow() < until


def muted_until(name: str, path: Path = _DEFAULT_STATE) -> Optional[str]:
    """Return the ISO timestamp when the mute expires, or None."""
    state = _load(path)
    entry = state.get(name)
    if entry is None:
        return None
    until = datetime.fromisoformat(entry["muted_until"])
    if _utcnow() >= until:
        return None
    return entry["muted_until"]
