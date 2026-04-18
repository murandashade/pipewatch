"""Tests for pipewatch.env_check."""
import os
import pytest
from unittest.mock import patch
from pipewatch.env_check import (
    check_pipeline_env,
    check_all_envs,
    format_env_check_text,
    EnvCheckResult,
)


def test_all_present():
    with patch.dict(os.environ, {"FOO": "1", "BAR": "2"}):
        r = check_pipeline_env("pipe", ["FOO", "BAR"])
    assert r.ok
    assert r.missing == []
    assert set(r.present) == {"FOO", "BAR"}


def test_some_missing():
    with patch.dict(os.environ, {"FOO": "1"}, clear=False):
        env = {k: v for k, v in os.environ.items() if k != "BAR"}
        with patch.dict(os.environ, env, clear=True):
            r = check_pipeline_env("pipe", ["FOO", "BAR"])
    assert not r.ok
    assert "BAR" in r.missing
    assert "FOO" in r.present


def test_empty_required():
    r = check_pipeline_env("pipe", [])
    assert r.ok
    assert r.missing == []


class _FakePipeline:
    def __init__(self, name, required_env=None):
        self.name = name
        self.required_env = required_env


def test_check_all_envs_skips_no_required():
    pipes = [_FakePipeline("a"), _FakePipeline("b", [])]
    results = check_all_envs(pipes)
    assert results == []


def test_check_all_envs_includes_required():
    with patch.dict(os.environ, {"MY_VAR": "x"}):
        pipes = [_FakePipeline("a", ["MY_VAR"]), _FakePipeline("b")]
        results = check_all_envs(pipes)
    assert len(results) == 1
    assert results[0].pipeline == "a"


def test_format_no_results():
    text = format_env_check_text([])
    assert "No environment" in text


def test_format_ok_result():
    r = EnvCheckResult(pipeline="pipe", present=["A"], missing=[])
    text = format_env_check_text([r])
    assert "[OK]" in text
    assert "+ A" in text


def test_format_fail_result():
    r = EnvCheckResult(pipeline="pipe", present=[], missing=["SECRET"])
    text = format_env_check_text([r])
    assert "[FAIL]" in text
    assert "- SECRET (missing)" in text
