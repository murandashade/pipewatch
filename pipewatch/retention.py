"""History retention: prune old run records from history files."""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def prune_history(
    hist_file: Path,
    max_age_days: Optional[int] = None,
    max_entries: Optional[int] = None,
) -> int:
    """Remove old entries from a history file.

    Returns the number of entries removed.
    """
    if not hist_file.exists():
        return 0

    lines = hist_file.read_text().splitlines()
    records = []
    for line in lines:
        line = line.strip()
        if line:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    original = len(records)

    if max_age_days is not None:
        cutoff = _utcnow() - timedelta(days=max_age_days)
        records = [
            r for r in records
            if datetime.fromisoformat(r["timestamp"]) >= cutoff
        ]

    if max_entries is not None and len(records) > max_entries:
        records = records[-max_entries:]

    hist_file.write_text("".join(json.dumps(r) + "\n" for r in records))
    return original - len(records)


def prune_all(
    history_dir: Path,
    max_age_days: Optional[int] = None,
    max_entries: Optional[int] = None,
) -> dict[str, int]:
    """Prune all *.jsonl history files in a directory."""
    results: dict[str, int] = {}
    for hist_file in sorted(history_dir.glob("*.jsonl")):
        removed = prune_history(hist_file, max_age_days=max_age_days, max_entries=max_entries)
        results[hist_file.stem] = removed
    return results
