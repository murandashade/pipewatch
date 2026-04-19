"""Runbook links: attach remediation URLs/notes to pipelines."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

_DEFAULT_FILE = "pipewatch_runbooks.json"


def _load(path: str) -> Dict[str, List[dict]]:
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(data: Dict[str, List[dict]], path: str) -> None:
    Path(path).write_text(json.dumps(data, indent=2))


def add_runbook(pipeline: str, url: str, note: str = "", path: str = _DEFAULT_FILE) -> dict:
    data = _load(path)
    entry = {"url": url, "note": note}
    data.setdefault(pipeline, []).append(entry)
    _save(data, path)
    return entry


def get_runbooks(pipeline: str, path: str = _DEFAULT_FILE) -> List[dict]:
    return _load(path).get(pipeline, [])


def remove_runbook(pipeline: str, url: str, path: str = _DEFAULT_FILE) -> bool:
    data = _load(path)
    entries = data.get(pipeline, [])
    new_entries = [e for e in entries if e["url"] != url]
    if len(new_entries) == len(entries):
        return False
    data[pipeline] = new_entries
    _save(data, path)
    return True


def all_runbooks(path: str = _DEFAULT_FILE) -> Dict[str, List[dict]]:
    return _load(path)


def format_runbooks_text(pipeline: str, entries: List[dict]) -> str:
    if not entries:
        return f"No runbooks for '{pipeline}'."
    lines = [f"Runbooks for '{pipeline}':"]
    for e in entries:
        note = f" — {e['note']}" if e.get("note") else ""
        lines.append(f"  {e['url']}{note}")
    return "\n".join(lines)
