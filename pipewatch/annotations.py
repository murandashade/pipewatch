"""Pipeline annotations: attach freeform notes to pipelines."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load(path: Path) -> Dict[str, List[dict]]:
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save(path: Path, data: Dict[str, List[dict]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def add_annotation(path: Path, pipeline: str, note: str, author: str = "") -> dict:
    data = _load(path)
    entry = {"note": note, "author": author, "timestamp": _utcnow()}
    data.setdefault(pipeline, []).append(entry)
    _save(path, data)
    return entry


def get_annotations(path: Path, pipeline: str) -> List[dict]:
    return _load(path).get(pipeline, [])


def delete_annotations(path: Path, pipeline: str) -> int:
    data = _load(path)
    count = len(data.pop(pipeline, []))
    _save(path, data)
    return count


def format_annotations_text(annotations: List[dict]) -> str:
    if not annotations:
        return "No annotations."
    lines = []
    for a in annotations:
        author = f" ({a['author']})" if a.get("author") else ""
        lines.append(f"[{a['timestamp']}]{author} {a['note']}")
    return "\n".join(lines)
