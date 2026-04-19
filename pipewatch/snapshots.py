"""Snapshot pipeline output for diffing against previous runs."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_DEFAULT_DIR = ".pipewatch/snapshots"


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _snapshot_path(base_dir: str, name: str) -> Path:
    return Path(base_dir) / f"{name}.json"


def _checksum(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def save_snapshot(name: str, output: str, base_dir: str = _DEFAULT_DIR) -> dict:
    """Persist output snapshot for a pipeline. Returns the saved record."""
    os.makedirs(base_dir, exist_ok=True)
    record = {
        "name": name,
        "timestamp": _utcnow(),
        "checksum": _checksum(output),
        "output": output,
    }
    _snapshot_path(base_dir, name).write_text(json.dumps(record))
    return record


def load_snapshot(name: str, base_dir: str = _DEFAULT_DIR) -> Optional[dict]:
    """Load the most recent snapshot for a pipeline, or None if absent."""
    p = _snapshot_path(base_dir, name)
    if not p.exists():
        return None
    return json.loads(p.read_text())


def has_changed(name: str, output: str, base_dir: str = _DEFAULT_DIR) -> bool:
    """Return True if output differs from the stored snapshot (or no snapshot exists)."""
    snap = load_snapshot(name, base_dir)
    if snap is None:
        return True
    return snap["checksum"] != _checksum(output)


def diff_summary(name: str, output: str, base_dir: str = _DEFAULT_DIR) -> str:
    """Human-readable summary of whether output changed."""
    snap = load_snapshot(name, base_dir)
    if snap is None:
        return f"{name}: no previous snapshot"
    if snap["checksum"] == _checksum(output):
        return f"{name}: output unchanged (since {snap['timestamp']})"
    return f"{name}: output changed since {snap['timestamp']}"
