"""Periodic digest report summarising pipeline run history."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pipewatch.history import load_history


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def build_digest(history_path: Path, since: datetime | None = None) -> dict[str, Any]:
    """Return a digest dict summarising runs in *history_path* since *since*."""
    records = load_history(history_path)
    if since is not None:
        records = [
            r for r in records
            if datetime.fromisoformat(r["timestamp"]) >= since
        ]

    total = len(records)
    failures = [r for r in records if not r.get("success", True)]
    successes = total - len(failures)

    pipelines: dict[str, dict[str, int]] = {}
    for r in records:
        name = r.get("pipeline", "unknown")
        entry = pipelines.setdefault(name, {"total": 0, "failures": 0})
        entry["total"] += 1
        if not r.get("success", True):
            entry["failures"] += 1

    return {
        "generated_at": _utcnow().isoformat(),
        "since": since.isoformat() if since else None,
        "total_runs": total,
        "successful_runs": successes,
        "failed_runs": len(failures),
        "pipelines": pipelines,
    }


def format_digest_text(digest: dict[str, Any]) -> str:
    """Render *digest* as a human-readable string."""
    lines = [
        "=== pipewatch digest ===",
        f"Generated : {digest['generated_at']}",
        f"Since     : {digest['since'] or 'all time'}",
        f"Runs      : {digest['total_runs']} total, "
        f"{digest['successful_runs']} ok, {digest['failed_runs']} failed",
        "",
        "Per-pipeline breakdown:",
    ]
    for name, stats in digest["pipelines"].items():
        lines.append(
            f"  {name}: {stats['total']} runs, {stats['failures']} failures"
        )
    return "\n".join(lines)
