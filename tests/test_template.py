"""Tests for pipewatch.template."""
import pytest
from pipewatch.template import (
    render,
    resolve_template,
    build_alert_message,
    DEFAULT_TEMPLATES,
)


def test_render_substitutes_known_keys():
    result = render("Hello {{ name }}!", {"name": "world"})
    assert result == "Hello world!"


def test_render_leaves_unknown_placeholders():
    result = render("Value: {{ missing }}", {})
    assert result == "Value: {{ missing }}"


def test_render_multiple_placeholders():
    tmpl = "{{a}} + {{b}} = {{c}}"
    assert render(tmpl, {"a": 1, "b": 2, "c": 3}) == "1 + 2 = 3"


def test_render_ignores_extra_context_keys():
    result = render("Hi {{ x }}", {"x": "there", "y": "unused"})
    assert result == "Hi there"


def test_resolve_template_returns_default():
    tmpl = resolve_template("failure")
    assert "{{pipeline}}" in tmpl


def test_resolve_template_custom_overrides_default():
    custom = {"failure": "ALERT: {{pipeline}} broke"}
    tmpl = resolve_template("failure", custom)
    assert tmpl == "ALERT: {{pipeline}} broke"


def test_resolve_template_custom_new_key():
    custom = {"warning": "Watch out: {{pipeline}}"}
    tmpl = resolve_template("warning", custom)
    assert tmpl == "Watch out: {{pipeline}}"


def test_resolve_template_unknown_raises():
    with pytest.raises(KeyError, match="unknown_event"):
        resolve_template("unknown_event")


def test_build_alert_message_failure():
    ctx = {"pipeline": "etl", "exit_code": 1, "stderr": "oops"}
    msg = build_alert_message("failure", ctx)
    assert "etl" in msg
    assert "1" in msg
    assert "oops" in msg


def test_build_alert_message_success():
    ctx = {"pipeline": "etl", "duration_s": 3.2}
    msg = build_alert_message("success", ctx)
    assert "etl" in msg
    assert "3.2" in msg


def test_build_alert_message_custom_template():
    custom = {"failure": "{{pipeline}} failed!"}
    msg = build_alert_message("failure", {"pipeline": "my_pipe"}, custom)
    assert msg == "my_pipe failed!"
