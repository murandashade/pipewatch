"""Tests for pipewatch.scheduler."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from pipewatch.scheduler import parse_cron, is_due, due_pipelines


_DT = datetime(2024, 6, 15, 14, 30, tzinfo=timezone.utc)  # Saturday, weekday=5


def test_parse_cron_valid():
    assert parse_cron('30 14 * * *') == ('30', '14', '*', '*', '*')


def test_parse_cron_invalid():
    with pytest.raises(ValueError):
        parse_cron('not a cron')


def test_parse_cron_too_few_fields():
    with pytest.raises(ValueError):
        parse_cron('* * *')


def test_is_due_wildcard():
    assert is_due('* * * * *', at=_DT) is True


def test_is_due_exact_match():
    assert is_due('30 14 15 6 5', at=_DT) is True


def test_is_due_wrong_minute():
    assert is_due('0 14 * * *', at=_DT) is False


def test_is_due_wrong_hour():
    assert is_due('30 9 * * *', at=_DT) is False


def test_is_due_wrong_dow():
    assert is_due('30 14 * * 0', at=_DT) is False  # Monday


def test_due_pipelines_returns_matching():
    p1 = MagicMock(schedule='30 14 * * *')
    p2 = MagicMock(schedule='0 9 * * *')
    p3 = MagicMock(schedule=None)
    cfg = MagicMock(pipelines=[p1, p2, p3])
    result = due_pipelines(cfg, at=_DT)
    assert result == [p1]


def test_due_pipelines_empty_when_none_match():
    p1 = MagicMock(schedule='0 0 1 1 *')
    cfg = MagicMock(pipelines=[p1])
    assert due_pipelines(cfg, at=_DT) == []


def test_due_pipelines_skips_no_schedule():
    p = MagicMock(spec=['name'])  # no schedule attr
    cfg = MagicMock(pipelines=[p])
    assert due_pipelines(cfg, at=_DT) == []
