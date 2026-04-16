import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from pipewatch.config import PipelineConfig
from pipewatch.webhook import AlertPayload, send_webhook


@dataclass
class RunResult:
    pipeline_name: str
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def success(self) -> bool:
        return self.exit_code == 0


def run_pipeline(name: str, command: str, timeout: Optional[int] = None) -> RunResult:
    start = time.monotonic()
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        duration = time.monotonic() - start
        return RunResult(
            pipeline_name=name,
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            duration_seconds=round(duration, 3),
        )
    except subprocess.TimeoutExpired:
        duration = time.monotonic() - start
        return RunResult(
            pipeline_name=name,
            exit_code=-1,
            stdout="",
            stderr=f"Pipeline timed out after {timeout}s",
            duration_seconds=round(duration, 3),
        )


def handle_result(result: RunResult, config: PipelineConfig, default_webhook: Optional[str] = None) -> bool:
    """Send alert if pipeline failed. Returns True if alert was sent."""
    if result.success:
        return False

    webhook_url = config.webhook_url or default_webhook
    if not webhook_url:
        return False

    payload = AlertPayload(
        pipeline_name=result.pipeline_name,
        exit_code=result.exit_code,
        error_output=result.stderr or result.stdout,
        duration_seconds=result.duration_seconds,
        timestamp=result.timestamp,
    )
    send_webhook(webhook_url, payload)
    return True
