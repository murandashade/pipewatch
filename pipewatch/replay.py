"""Replay failed pipelines from history."""
from __future__ import annotations

from typing import List, Optional

from pipewatch.history import load_history
from pipewatch.monitor import RunResult, run_pipeline
from pipewatch.config import PipelineConfig


def failed_runs(history_file: str, pipeline_name: Optional[str] = None) -> List[dict]:
    """Return history entries that represent failures."""
    entries = load_history(history_file)
    failures = [e for e in entries if not e.get("success", True)]
    if pipeline_name:
        failures = [e for e in failures if e.get("pipeline") == pipeline_name]
    return failures


def replay_pipeline(cfg: PipelineConfig) -> RunResult:
    """Re-run a single pipeline and return the result."""
    return run_pipeline(cfg)


def replay_failures(
    configs: List[PipelineConfig],
    history_file: str,
    pipeline_name: Optional[str] = None,
) -> List[RunResult]:
    """Replay every pipeline that has at least one failure in history.

    Args:
        configs: All known pipeline configurations.
        history_file: Path to the JSONL history file.
        pipeline_name: If given, only replay that pipeline.

    Returns:
        List of RunResult for each replayed pipeline.
    """
    failures = failed_runs(history_file, pipeline_name)
    failed_names = {e["pipeline"] for e in failures}
    to_run = [c for c in configs if c.name in failed_names]
    return [replay_pipeline(c) for c in to_run]
