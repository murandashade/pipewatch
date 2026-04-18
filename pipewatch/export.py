"""Export pipeline history to CSV or JSON formats."""
from __future__ import annotations

import csv
import io
import json
from typing import List, Dict, Any

from pipewatch.history import load_history


def export_json(history_file: str, pipeline: str | None = None) -> str:
    """Return history records as a JSON string."""
    records = _filtered(history_file, pipeline)
    return json.dumps(records, indent=2)


def export_csv(history_file: str, pipeline: str | None = None) -> str:
    """Return history records as a CSV string."""
    records = _filtered(history_file, pipeline)
    if not records:
        return ""
    buf = io.StringIO()
    fieldnames = ["pipeline", "timestamp", "success", "exit_code", "duration_s"]
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in records:
        writer.writerow(row)
    return buf.getvalue()


def _filtered(history_file: str, pipeline: str | None) -> List[Dict[str, Any]]:
    records = load_history(history_file)
    if pipeline:
        records = [r for r in records if r.get("pipeline") == pipeline]
    return records
