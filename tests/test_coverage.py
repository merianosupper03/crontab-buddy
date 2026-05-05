"""Tests for crontab_buddy.coverage."""

import pytest
from crontab_buddy.coverage import compute_coverage, format_coverage, _hours_covered
from crontab_buddy.parser import CronExpression


def test_every_minute_covers_all_hours():
    result = compute_coverage(["* * * * *"])
    assert result["coverage_percent"] == 100.0
    assert len(result["covered_hours"]) == 24
    assert result["uncovered_hours"] == []


def test_single_hour_covers_one_hour():
    result = compute_coverage(["0 3 * * *"])
    assert 3 in result["covered_hours"]
    assert len(result["covered_hours"]) == 1
    assert result["coverage_percent"] == pytest.approx(100 / 24 * 100, rel=0.01)


def test_invalid_expression_counted():
    result = compute_coverage(["not a cron", "* * * * *"])
    assert result["invalid"] == 1
    assert result["valid"] == 1


def test_multiple_expressions_union_hours():
    result = compute_coverage(["0 6 * * *", "0 18 * * *"])
    assert 6 in result["covered_hours"]
    assert 18 in result["covered_hours"]
    assert len(result["covered_hours"]) == 2


def test_step_expression_covers_every_other_hour():
    result = compute_coverage(["0 */2 * * *"])
    assert result["covered_hours"] == [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]


def test_range_expression_covers_range():
    result = compute_coverage(["0 9-17 * * *"])
    assert result["covered_hours"] == list(range(9, 18))


def test_list_expression_covers_listed_hours():
    result = compute_coverage(["0 8,12,20 * * *"])
    assert 8 in result["covered_hours"]
    assert 12 in result["covered_hours"]
    assert 20 in result["covered_hours"]
    assert len(result["covered_hours"]) == 3


def test_empty_expressions_zero_coverage():
    result = compute_coverage([])
    assert result["coverage_percent"] == 0.0
    assert result["covered_hours"] == []
    assert len(result["uncovered_hours"]) == 24


def test_hour_counts_incremented_correctly():
    result = compute_coverage(["0 6 * * *", "0 6 * * *"])
    assert result["hour_counts"][6] == 2
    assert result["hour_counts"][7] == 0


def test_format_coverage_contains_percent():
    result = compute_coverage(["* * * * *"])
    out = format_coverage(result)
    assert "100.0%" in out


def test_format_coverage_shows_uncovered():
    result = compute_coverage(["0 0 * * *"])
    out = format_coverage(result)
    assert "Uncovered hours" in out


def test_format_coverage_all_covered_message():
    result = compute_coverage(["* * * * *"])
    out = format_coverage(result)
    assert "All 24 hours are covered" in out
