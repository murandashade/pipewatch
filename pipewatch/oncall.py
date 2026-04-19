"""On-call schedule: map pipelines to responsible contacts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _load(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save(path: str, data: dict) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_oncall(path: str, pipeline: str, contacts: List[str]) -> None:
    """Set the on-call contacts for a pipeline."""
    data = _load(path)
    data[pipeline] = contacts
    _save(path, data)


def get_oncall(path: str, pipeline: str) -> List[str]:
    """Return contacts for a pipeline, or empty list if none set."""
    return _load(path).get(pipeline, [])


def remove_oncall(path: str, pipeline: str) -> bool:
    """Remove on-call entry. Returns True if it existed."""
    data = _load(path)
    if pipeline not in data:
        return False
    del data[pipeline]
    _save(path, data)
    return True


def all_oncall(path: str) -> Dict[str, List[str]]:
    """Return the full on-call mapping."""
    return _load(path)


def format_oncall_text(pipeline: str, contacts: List[str]) -> str:
    if not contacts:
        return f"{pipeline}: (no on-call contacts set)"
    joined = ", ".join(contacts)
    return f"{pipeline}: {joined}"
