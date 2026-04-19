"""Audit log: record and query configuration change events."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import List, Optional


DEFAULT_AUDIT_FILE = "pipewatch_audit.jsonl"


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_event(
    audit_file: str,
    event_type: str,
    pipeline: Optional[str],
    detail: str,
    actor: Optional[str] = None,
) -> dict:
    """Append a single audit event to *audit_file* and return it."""
    entry = {
        "timestamp": _utcnow(),
        "event_type": event_type,
        "pipeline": pipeline,
        "detail": detail,
        "actor": actor or os.environ.get("USER", "unknown"),
    }
    os.makedirs(os.path.dirname(os.path.abspath(audit_file)), exist_ok=True)
    with open(audit_file, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    return entry


def load_events(audit_file: str) -> List[dict]:
    """Return all audit events from *audit_file*, oldest first."""
    if not os.path.exists(audit_file):
        return []
    events = []
    with open(audit_file, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def events_for_pipeline(audit_file: str, pipeline: str) -> List[dict]:
    """Return audit events filtered to a specific pipeline name."""
    return [e for e in load_events(audit_file) if e.get("pipeline") == pipeline]


def format_audit_text(events: List[dict]) -> str:
    """Return a human-readable summary of *events*."""
    if not events:
        return "No audit events found."
    lines = []
    for e in events:
        pipeline_part = f"[{e['pipeline']}] " if e.get("pipeline") else ""
        lines.append(
            f"{e['timestamp']}  {e['event_type']:20s}  {pipeline_part}{e['detail']}  (actor={e['actor']})"
        )
    return "\n".join(lines)
