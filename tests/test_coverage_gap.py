"""Tests for crontab_buddy.coverage_gap."""

import pytest
from crontab_buddy.coverage_gap import find_coverage_gaps, format_coverage_gap


def test_empty_list_has_all_gaps():
    result = find_coverage_gaps([])
    assert result["gap_count"] == 24
    assert result["fully_covered"] is False
    assert result["covered_hours"] == []


def test_every_minute_covers_all_hours():
    result = find_coverage_gaps(["* * * * *"])
    assert result["fully_covered"] is True
    assert result["gap_count"] == 0
    assert len(result["covered_hours"]) == 24


def test_single_hour_leaves_23_gaps():
    result = find_coverage_gaps(["0 9 * * *"])
    assert 9 in result["covered_hours"]
    assert result["gap_count"] == 23
    assert 9 not in result["gap_hours"]


def test_two_expressions_union_hours():
    result = find_coverage_gaps(["0 8 * * *", "0 20 * * *"])
    assert 8 in result["covered_hours"]
    assert 20 in result["covered_hours"]
    assert result["gap_count"] == 22


def test_range_hour_covers_range():
    result = find_coverage_gaps(["0 9-17 * * *"])
    for h in range(9, 18):
        assert h in result["covered_hours"]
    assert result["gap_count"] == 24 - 9


def test_step_hour_covers_every_other():
    result = find_coverage_gaps(["0 */6 * * *"])
    assert 0 in result["covered_hours"]
    assert 6 in result["covered_hours"]
    assert 12 in result["covered_hours"]
    assert 18 in result["covered_hours"]
    assert result["gap_count"] == 20


def test_invalid_expression_counted():
    result = find_coverage_gaps(["not_a_cron", "0 10 * * *"])
    assert "not_a_cron" in result["invalid"]
    assert result["valid_count"] == 1
    assert 10 in result["covered_hours"]


def test_fully_covered_flag_false_when_gaps():
    result = find_coverage_gaps(["0 0 * * *"])
    assert result["fully_covered"] is False


def test_format_shows_gap_hours(capsys):
    result = find_coverage_gaps(["0 9 * * *"])
    output = format_coverage_gap(result)
    assert "Gap hours" in output
    assert "9" not in output.split("Gap hours")[-1].split("\n")[0]


def test_format_full_coverage_message():
    result = find_coverage_gaps(["* * * * *"])
    output = format_coverage_gap(result)
    assert "FULL" in output
    assert "no gaps" in output


def test_format_shows_invalid():
    result = find_coverage_gaps(["bad_expr"])
    output = format_coverage_gap(result)
    assert "bad_expr" in output


def test_list_expression_in_hour():
    result = find_coverage_gaps(["0 8,12,18 * * *"])
    assert 8 in result["covered_hours"]
    assert 12 in result["covered_hours"]
    assert 18 in result["covered_hours"]
    assert result["gap_count"] == 21
