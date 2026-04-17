"""Configuration loading and validation for pipewatch."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from pipewatch.alert_policy import AlertPolicy


@dataclass
class PipelineConfig:
    name: str
    command: str
    webhook: Optional[str] = None
    timeout: int = 60
    policy: AlertPolicy = field(default_factory=AlertPolicy)


@dataclass
class AppConfig:
    pipelines: List[PipelineConfig]
    default_webhook: Optional[str] = None
    history_path: str = "pipewatch_history.jsonl"


def _parse_policy(raw: Dict[str, Any]) -> AlertPolicy:
    return AlertPolicy(
        min_streak=raw.get("min_streak", 1),
        cooldown_minutes=raw.get("cooldown_minutes", 0),
    )


def load_config(path: str) -> AppConfig:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)

    default_webhook = data.get("default_webhook")
    history_path = data.get("history_path", "pipewatch_history.jsonl")

    pipelines = []
    for raw in data.get("pipelines", []):
        policy_raw = raw.get("alert_policy", data.get("alert_policy", {}))
        pipelines.append(
            PipelineConfig(
                name=raw["name"],
                command=raw["command"],
                webhook=raw.get("webhook", default_webhook),
                timeout=raw.get("timeout", 60),
                policy=_parse_policy(policy_raw),
            )
        )

    return AppConfig(
        pipelines=pipelines,
        default_webhook=default_webhook,
        history_path=history_path,
    )


def validate_config(cfg: AppConfig) -> List[str]:
    errors: List[str] = []
    names = [p.name for p in cfg.pipelines]
    if len(names) != len(set(names)):
        errors.append("Duplicate pipeline names detected.")
    for p in cfg.pipelines:
        if not p.command.strip():
            errors.append(f"Pipeline '{p.name}' has an empty command.")
        if p.timeout <= 0:
            errors.append(f"Pipeline '{p.name}' timeout must be > 0.")
    return errors
