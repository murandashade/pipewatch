"""Simple alert message templating for webhook payloads."""
from __future__ import annotations

import re
from typing import Any

_VARIABLE_RE = re.compile(r"\{\{\s*(\w+)\s*\}\}")

DEFAULT_TEMPLATES = {
    "failure": "Pipeline '{{pipeline}}' failed (exit {{exit_code}}): {{stderr}}",
    "success": "Pipeline '{{pipeline}}' completed successfully in {{duration_s}}s.",
    "timeout": "Pipeline '{{pipeline}}' timed out after {{duration_s}}s.",
}


def render(template: str, context: dict[str, Any]) -> str:
    """Render *template* by substituting ``{{ key }}`` placeholders from *context*.

    Unknown placeholders are left unchanged.
    """
    def _replace(m: re.Match) -> str:  # type: ignore[type-arg]
        key = m.group(1)
        return str(context[key]) if key in context else m.group(0)

    return _VARIABLE_RE.sub(_replace, template)


def resolve_template(template_name: str, custom_templates: dict[str, str] | None = None) -> str:
    """Return the template string for *template_name*.

    *custom_templates* (from config) takes precedence over built-in defaults.
    Raises ``KeyError`` when the name is unknown in both sources.
    """
    merged = {**DEFAULT_TEMPLATES, **(custom_templates or {})}
    if template_name not in merged:
        raise KeyError(f"Unknown alert template: '{template_name}'")
    return merged[template_name]


def build_alert_message(
    event: str,
    context: dict[str, Any],
    custom_templates: dict[str, str] | None = None,
) -> str:
    """Convenience wrapper: resolve template for *event* then render with *context*."""
    tmpl = resolve_template(event, custom_templates)
    return render(tmpl, context)
