"""Tests for cron expression parsing and humanization."""

import pytest
from crontab_buddy.parser import parse, CronParseError
from crontab_buddy.humanizer import humanize


def test_parse_basic():
    expr = parse("0 9 * * 1")
    assert expr.minute == "0"
    assert expr.hour == "9"
    assert expr.day_of_week == "1"


def test_parse_wrong_field_count():
    with pytest.raises(CronParseError, match="Expected 5 fields"):
        parse("* * *")


def test_parse_out_of_range_minute():
    with pytest.raises(CronParseError):
        parse("60 * * * *")


def test_parse_out_of_range_hour():
    with pytest.raises(CronParseError):
        parse("0 25 * * *")


def test_parse_step_expression():
    expr = parse("*/15 * * * *")
    assert expr.minute == "*/15"


def test_parse_range():
    expr = parse("0 9-17 * * 1-5")
    assert expr.hour == "9-17"
    assert expr.day_of_week == "1-5"


def test_parse_list():
    expr = parse("0 8,12,18 * * *")
    assert expr.hour == "8,12,18"


def test_humanize_every_minute():
    expr = parse("* * * * *")
    result = humanize(expr)
    assert "Every minute" in result


def test_humanize_daily_at_nine():
    expr = parse("0 9 * * *")
    result = humanize(expr)
    assert "9" in result
    assert "start" in result.lower() or "0" in result


def test_humanize_weekday():
    expr = parse("0 9 * * 1")
    result = humanize(expr)
    assert "Monday" in result


def test_humanize_monthly():
    expr = parse("0 0 1 1 *")
    result = humanize(expr)
    assert "January" in result


def test_humanize_step():
    expr = parse("*/15 * * * *")
    result = humanize(expr)
    assert "15" in result
