"""High-level entry point: load config, run all pipelines, handle alerts."""
import sys
from typing import List, Optional

from pipewatch.config import AppConfig, load_config, validate_config
from pipewatch.monitor import RunResult, handle_result, run_pipeline


def run_all(config_path: str) -> List[RunResult]:
    config: AppConfig = load_config(config_path)
    validate_config(config)

    results: List[RunResult] = []
    for pipeline in config.pipelines:
        print(f"[pipewatch] Running pipeline: {pipeline.name}")
        result = run_pipeline(
            name=pipeline.name,
            command=pipeline.command,
            timeout=pipeline.timeout,
        )
        status = "OK" if result.success else "FAILED"
        print(f"[pipewatch] {pipeline.name} -> {status} (exit={result.exit_code}, {result.duration_seconds}s)")

        alert_sent = handle_result(result, pipeline, default_webhook=config.default_webhook_url)
        if not result.success and alert_sent:
            print(f"[pipewatch] Alert sent for {pipeline.name}")
        elif not result.success:
            print(f"[pipewatch] No webhook configured for {pipeline.name}, skipping alert")

        results.append(result)

    return results


def summarise(results: List[RunResult]) -> int:
    """Print summary and return exit code (0 = all passed, 1 = any failed)."""
    failed = [r for r in results if not r.success]
    total = len(results)
    print(f"\n[pipewatch] {total - len(failed)}/{total} pipelines succeeded.")
    if failed:
        print("[pipewatch] Failed pipelines: " + ", ".join(r.pipeline_name for r in failed))
        return 1
    return 0
