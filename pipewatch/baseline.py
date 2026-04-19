"""Baseline duration tracking: record and compare pipeline run durations."""

from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Optional

DEFAULT_BASELINE_FILE = ".pipewatch_baseline.json"


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save(path: Path, data: dict) -> None:
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def record_duration(name: str, duration: float, baseline_file: str = DEFAULT_BASELINE_FILE) -> None:
    """Append a duration sample for a pipeline."""
    path = Path(baseline_file)
    data = _load(path)
    data.setdefault(name, [])
    data[name].append(round(duration, 3))
    _save(path, data)


def get_baseline(name: str, baseline_file: str = DEFAULT_BASELINE_FILE) -> Optional[float]:
    """Return the mean duration for a pipeline, or None if no data."""
    data = _load(Path(baseline_file))
    samples = data.get(name, [])
    return round(statistics.mean(samples), 3) if samples else None


def is_slow(name: str, duration: float, threshold: float = 2.0,
            baseline_file: str = DEFAULT_BASELINE_FILE) -> bool:
    """Return True if duration exceeds threshold * baseline mean."""
    baseline = get_baseline(name, baseline_file)
    if baseline is None or baseline == 0:
        return False
    return duration > baseline * threshold


def format_baseline_text(name: str, baseline_file: str = DEFAULT_BASELINE_FILE) -> str:
    data = _load(Path(baseline_file))
    samples = data.get(name, [])
    if not samples:
        return f"{name}: no baseline data"
    mean = statistics.mean(samples)
    stdev = statistics.stdev(samples) if len(samples) > 1 else 0.0
    return (
        f"{name}: samples={len(samples)} mean={mean:.3f}s "
        f"stdev={stdev:.3f}s min={min(samples):.3f}s max={max(samples):.3f}s"
    )
