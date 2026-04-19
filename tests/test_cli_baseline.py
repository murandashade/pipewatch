"""Tests for pipewatch.cli_baseline."""

import pytest
from pipewatch.cli_baseline import handle_baseline


class _Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


@pytest.fixture
def bf(tmp_path):
    return str(tmp_path / "baseline.json")


def test_record_returns_zero(bf, capsys):
    args = _Args(baseline_cmd="record", pipeline="etl", duration=3.5, baseline_file=bf)
    assert handle_baseline(args) == 0
    out = capsys.readouterr().out
    assert "3.5" in out


def test_show_no_data(bf, capsys):
    args = _Args(baseline_cmd="show", pipeline="etl", baseline_file=bf)
    assert handle_baseline(args) == 0
    assert "no baseline data" in capsys.readouterr().out


def test_show_with_data(bf, capsys):
    from pipewatch.baseline import record_duration
    record_duration("etl", 2.0, bf)
    record_duration("etl", 4.0, bf)
    args = _Args(baseline_cmd="show", pipeline="etl", baseline_file=bf)
    handle_baseline(args)
    assert "mean=3.000s" in capsys.readouterr().out


def test_check_no_baseline_returns_one(bf, capsys):
    args = _Args(baseline_cmd="check", pipeline="etl", duration=5.0,
                 threshold=2.0, baseline_file=bf)
    assert handle_baseline(args) == 1


def test_check_ok_returns_zero(bf, capsys):
    from pipewatch.baseline import record_duration
    record_duration("etl", 2.0, bf)
    args = _Args(baseline_cmd="check", pipeline="etl", duration=3.0,
                 threshold=2.0, baseline_file=bf)
    assert handle_baseline(args) == 0
    assert "OK" in capsys.readouterr().out


def test_check_slow_returns_two(bf, capsys):
    from pipewatch.baseline import record_duration
    record_duration("etl", 2.0, bf)
    args = _Args(baseline_cmd="check", pipeline="etl", duration=10.0,
                 threshold=2.0, baseline_file=bf)
    assert handle_baseline(args) == 2
    assert "SLOW" in capsys.readouterr().out
