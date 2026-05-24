"""Tests for cadence_gap module and CLI commands."""
import json
import pytest
from crontab_buddy.cadence_gap import find_cadence_gaps, format_cadence_gap
from crontab_buddy.cadence_gap_cli import (
    cmd_cadence_gap_check,
    cmd_cadence_gap_hours,
    cmd_cadence_gap_percent,
    cmd_cadence_gap_json,
)


class Args:
    def __init__(self, expressions):
        self.expressions = expressions


def test_empty_list_has_all_gaps():
    result = find_cadence_gaps([])
    assert result["gap_hours"] == list(range(24))
    assert result["coverage_percent"] == 0.0
    assert result["has_gaps"] is True


def test_every_minute_covers_all_hours():
    result = find_cadence_gaps(["* * * * *"])
    assert result["gap_hours"] == []
    assert result["coverage_percent"] == 100.0
    assert result["has_gaps"] is False


def test_single_hour_expression_leaves_gaps():
    result = find_cadence_gaps(["0 9 * * *"])
    assert 9 in result["covered_hours"]
    assert len(result["gap_hours"]) == 23


def test_two_expressions_union_coverage():
    result = find_cadence_gaps(["0 9 * * *", "0 18 * * *"])
    assert 9 in result["covered_hours"]
    assert 18 in result["covered_hours"]
    assert len(result["gap_hours"]) == 22


def test_range_hour_covers_range():
    result = find_cadence_gaps(["0 8-12 * * *"])
    for h in range(8, 13):
        assert h in result["covered_hours"]
    assert len(result["gap_hours"]) == 19


def test_step_hour_covers_evens():
    result = find_cadence_gaps(["0 */2 * * *"])
    for h in range(0, 24, 2):
        assert h in result["covered_hours"]
    assert all(h % 2 == 1 for h in result["gap_hours"])


def test_invalid_expression_ignored():
    result = find_cadence_gaps(["not_valid", "0 6 * * *"])
    assert 6 in result["covered_hours"]


def test_format_shows_coverage_percent():
    result = find_cadence_gaps(["0 12 * * *"])
    text = format_cadence_gap(result)
    assert "Coverage:" in text


def test_format_no_gaps_message():
    result = find_cadence_gaps(["* * * * *"])
    text = format_cadence_gap(result)
    assert "No gaps" in text


def test_cmd_check_prints_output(capsys):
    cmd_cadence_gap_check(Args(["0 9 * * *"]))
    out = capsys.readouterr().out
    assert "Coverage:" in out


def test_cmd_hours_no_gaps(capsys):
    cmd_cadence_gap_hours(Args(["* * * * *"]))
    out = capsys.readouterr().out
    assert out.strip() == "none"


def test_cmd_percent_prints_float(capsys):
    cmd_cadence_gap_percent(Args(["0 6 * * *"]))
    out = capsys.readouterr().out
    assert float(out.strip()) < 100.0


def test_cmd_json_is_valid(capsys):
    cmd_cadence_gap_json(Args(["0 0 * * *"]))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "gap_hours" in data
    assert "coverage_percent" in data
