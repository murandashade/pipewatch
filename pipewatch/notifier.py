"""Throttled notification dispatch with cooldown support."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Optional

from pipewatch.webhook import AlertPayload, send_webhook

DEFAULT_COOLDOWN = 300  # seconds


def _state_path(base_dir: str, pipeline_name: str) -> Path:
    return Path(base_dir) / f".notify_state_{pipeline_name}.json"


def _load_state(state_file: Path) -> dict:
    if state_file.exists():
        try:
            return json.loads(state_file.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_state(state_file: Path, data: dict) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(data))


def is_on_cooldown(
    pipeline_name: str,
    cooldown: int = DEFAULT_COOLDOWN,
    base_dir: str = ".",
) -> bool:
    """Return True if the pipeline is within its notification cooldown window."""
    state_file = _state_path(base_dir, pipeline_name)
    state = _load_state(state_file)
    last_sent = state.get("last_sent")
    if last_sent is None:
        return False
    return (time.time() - last_sent) < cooldown


def notify(
    payload: AlertPayload,
    webhook_url: str,
    cooldown: int = DEFAULT_COOLDOWN,
    base_dir: str = ".",
) -> bool:
    """Send a webhook notification unless the pipeline is on cooldown.

    Returns True if the notification was sent, False if suppressed.
    """
    name = payload.pipeline_name
    if is_on_cooldown(name, cooldown=cooldown, base_dir=base_dir):
        return False

    send_webhook(webhook_url, payload)

    state_file = _state_path(base_dir, name)
    _save_state(state_file, {"last_sent": time.time()})
    return True
