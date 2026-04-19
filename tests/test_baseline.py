"""Tests for pipewatch.baseline."""

import pytest
from pathlib import Path

from pipewatch.baseline import (
    record_duration,
    get_baseline,
    is_slow,
    format_baseline_text,
)


@pytest.fixture
def bf(tmp_path):
    return str(tmp_path / "baseline.json")


def test_get_baseline_missing_returns_none(bf):
    assert get_baseline("pipe", bf) is None


def test_record_and_get_baseline(bf):
    record_duration("pipe", 1.0, bf)
    record_duration("pipe", 3.0, bf)
    assert get_baseline("pipe", bf) == 2.0


def test_record_multiple_pipelines(bf):
    record_duration("a", 1.0, bf)
    record_duration("b", 5.0, bf)
    assert get_baseline("a", bf) == 1.0
    assert get_baseline("b", bf) == 5.0


def test_is_slow_no_baseline_returns_false(bf):
    assert is_slow("pipe", 999.0, baseline_file=bf) is False


def test_is_slow_below_threshold(bf):
    record_duration("pipe", 2.0, bf)
    record_duration("pipe", 2.0, bf)
    assert is_slow("pipe", 3.5, threshold=2.0, baseline_file=bf) is False


def test_is_slow_above_threshold(bf):
    record_duration("pipe", 2.0, bf)
    record_duration("pipe", 2.0, bf)
    assert is_slow("pipe", 5.0, threshold=2.0, baseline_file=bf) is True


def test_format_baseline_text_no_data(bf):
    result = format_baseline_text("pipe", bf)
    assert "no baseline data" in result


def test_format_baseline_text_with_data(bf):
    for d in [1.0, 2.0, 3.0]:
        record_duration("pipe", d, bf)
    result = format_baseline_text("pipe", bf)
    assert "samples=3" in result
    assert "mean=2.000s" in result
