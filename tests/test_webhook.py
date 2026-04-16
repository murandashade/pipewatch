import json
from unittest.mock import MagicMock, patch

import pytest

from pipewatch.webhook import AlertPayload, send_webhook


@pytest.fixture
def payload():
    return AlertPayload(
        pipeline_name="ingest_orders",
        status="failure",
        message="Process exited with code 1",
        exit_code=1,
        timestamp="2024-01-15T12:00:00+00:00",
    )


def test_payload_to_dict(payload):
    d = payload.to_dict()
    assert d["pipeline"] == "ingest_orders"
    assert d["status"] == "failure"
    assert d["exit_code"] == 1
    assert d["timestamp"] == "2024-01-15T12:00:00+00:00"


def test_payload_timestamp_defaults_when_none():
    p = AlertPayload(pipeline_name="p", status="failure", message="err")
    d = p.to_dict()
    assert "timestamp" in d and d["timestamp"] is not None


def _mock_response(status_code: int):
    resp = MagicMock()
    resp.status = status_code
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def test_send_webhook_success(payload):
    with patch("urllib.request.urlopen", return_value=_mock_response(200)) as mock_open:
        result = send_webhook("https://example.com/hook", payload)
    assert result is True
    mock_open.assert_called_once()


def test_send_webhook_http_error(payload):
    import urllib.error

    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.HTTPError(None, 500, "Server Error", {}, None),
    ):
        result = send_webhook("https://example.com/hook", payload)
    assert result is False


def test_send_webhook_url_error(payload):
    import urllib.error

    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.URLError("connection refused"),
    ):
        result = send_webhook("https://example.com/hook", payload)
    assert result is False


def test_send_webhook_posts_json(payload):
    captured = {}

    def fake_urlopen(req, timeout):
        captured["body"] = json.loads(req.data.decode())
        captured["content_type"] = req.get_header("Content-type")
        return _mock_response(204)

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        send_webhook("https://example.com/hook", payload)

    assert captured["content_type"] == "application/json"
    assert captured["body"]["pipeline"] == "ingest_orders"
