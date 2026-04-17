"""Tests for the next_runs scheduler."""

from datetime import datetime
import pytest

from crontab_buddy.parser import CronExpression
from crontab_buddy.scheduler import next_runs, _matches_field


def test_matches_field_wildcard():
    assert _matches_field(30, "*", 0, 59) is True


def test_matches_field_exact():
    assert _matches_field(5, "5", 0, 59) is True
    assert _matches_field(6, "5", 0, 59) is False


def test_matches_field_range():
    assert _matches_field(3, "1-5", 0, 59) is True
    assert _matches_field(6, "1-5", 0, 59) is False


def test_matches_field_list():
    assert _matches_field(15, "5,15,45", 0, 59) is True
    assert _matches_field(20, "5,15,45", 0, 59) is False


def test_matches_field_step():
    assert _matches_field(0, "*/15", 0, 59) is True
    assert _matches_field(15, "*/15", 0, 59) is True
    assert _matches_field(7, "*/15", 0, 59) is False


def test_next_runs_count():
    expr = CronExpression("* * * * *")
    anchor = datetime(2024, 1, 1, 12, 0)
    runs = next_runs(expr, count=5, after=anchor)
    assert len(runs) == 5


def test_next_runs_every_minute():
    expr = CronExpression("* * * * *")
    anchor = datetime(2024, 1, 1, 12, 0)
    runs = next_runs(expr, count=3, after=anchor)
    assert runs[0] == datetime(2024, 1, 1, 12, 1)
    assert runs[1] == datetime(2024, 1, 1, 12, 2)
    assert runs[2] == datetime(2024, 1, 1, 12, 3)


def test_next_runs_hourly():
    expr = CronExpression("0 * * * *")
    anchor = datetime(2024, 1, 1, 12, 0)
    runs = next_runs(expr, count=3, after=anchor)
    assert all(r.minute == 0 for r in runs)
    assert runs[0] == datetime(2024, 1, 1, 13, 0)


def test_next_runs_daily_midnight():
    expr = CronExpression("0 0 * * *")
    anchor = datetime(2024, 1, 1, 0, 0)
    runs = next_runs(expr, count=2, after=anchor)
    assert runs[0] == datetime(2024, 1, 2, 0, 0)
    assert runs[1] == datetime(2024, 1, 3, 0, 0)


def test_next_runs_specific_time():
    expr = CronExpression("30 9 * * *")
    anchor = datetime(2024, 6, 1, 8, 0)
    runs = next_runs(expr, count=1, after=anchor)
    assert runs[0] == datetime(2024, 6, 1, 9, 30)
