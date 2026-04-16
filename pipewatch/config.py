"""Configuration loading and validation for pipewatch."""

import os
import json
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PipelineConfig:
    name: str
    webhook_url: str
    alert_on: List[str] = field(default_factory=lambda: ["failure"])
    retry_count: int = 0
    timeout_seconds: int = 30
    tags: List[str] = field(default_factory=list)


@dataclass
class AppConfig:
    pipelines: List[PipelineConfig] = field(default_factory=list)
    default_webhook_url: Optional[str] = None
    log_level: str = "INFO"


def load_config(path: str) -> AppConfig:
    """Load and parse configuration from a JSON file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r") as f:
        raw = json.load(f)

    pipelines = [
        PipelineConfig(
            name=p["name"],
            webhook_url=p.get("webhook_url", raw.get("default_webhook_url", "")),
            alert_on=p.get("alert_on", ["failure"]),
            retry_count=p.get("retry_count", 0),
            timeout_seconds=p.get("timeout_seconds", 30),
            tags=p.get("tags", []),
        )
        for p in raw.get("pipelines", [])
    ]

    return AppConfig(
        pipelines=pipelines,
        default_webhook_url=raw.get("default_webhook_url"),
        log_level=raw.get("log_level", "INFO"),
    )


def validate_config(config: AppConfig) -> List[str]:
    """Return a list of validation error messages, empty if valid."""
    errors = []
    for pipeline in config.pipelines:
        if not pipeline.name:
            errors.append("Pipeline entry is missing a name.")
        if not pipeline.webhook_url:
            errors.append(f"Pipeline '{pipeline.name}' has no webhook_url and no default is set.")
        valid_events = {"failure", "success", "timeout"}
        for event in pipeline.alert_on:
            if event not in valid_events:
                errors.append(f"Pipeline '{pipeline.name}' has unknown alert event: '{event}'.")
    return errors
