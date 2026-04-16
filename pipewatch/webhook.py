import json
import logging
import urllib.request
import urllib.error
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class AlertPayload:
    pipeline_name: str
    status: str
    message: str
    exit_code: Optional[int] = None
    timestamp: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "pipeline": self.pipeline_name,
            "status": self.status,
            "message": self.message,
            "exit_code": self.exit_code,
            "timestamp": self.timestamp or datetime.now(timezone.utc).isoformat(),
        }


def send_webhook(url: str, payload: AlertPayload, timeout: int = 10) -> bool:
    """Send an alert payload to a webhook URL.

    Returns True on success, False on failure.
    """
    data = json.dumps(payload.to_dict()).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            logger.info("Webhook delivered to %s (HTTP %s)", url, status)
            return 200 <= status < 300
    except urllib.error.HTTPError as exc:
        logger.error("Webhook HTTP error for %s: %s %s", url, exc.code, exc.reason)
    except urllib.error.URLError as exc:
        logger.error("Webhook URL error for %s: %s", url, exc.reason)
    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error sending webhook to %s: %s", url, exc)
    return False
