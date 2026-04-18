"""Environment variable validation for pipelines."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class EnvCheckResult:
    pipeline: str
    missing: List[str] = field(default_factory=list)
    present: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.missing) == 0


def check_pipeline_env(pipeline_name: str, required_vars: List[str]) -> EnvCheckResult:
    """Check that all required env vars are set for a pipeline."""
    result = EnvCheckResult(pipeline=pipeline_name)
    for var in required_vars:
        if os.environ.get(var) is not None:
            result.present.append(var)
        else:
            result.missing.append(var)
    return result


def check_all_envs(pipelines: list) -> List[EnvCheckResult]:
    """Run env checks for all pipelines that declare required_env."""
    results = []
    for p in pipelines:
        required = getattr(p, "required_env", None) or []
        if required:
            results.append(check_pipeline_env(p.name, required))
    return results


def format_env_check_text(results: List[EnvCheckResult]) -> str:
    if not results:
        return "No environment checks defined."
    lines = []
    for r in results:
        status = "OK" if r.ok else "FAIL"
        lines.append(f"[{status}] {r.pipeline}")
        for v in r.present:
            lines.append(f"  + {v}")
        for v in r.missing:
            lines.append(f"  - {v} (missing)")
    return "\n".join(lines)
