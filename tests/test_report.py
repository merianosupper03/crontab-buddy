"""Tests for crontab_buddy/report.py"""

import pytest
from crontab_buddy.report import build_report, format_report


VALID_EXPR = "0 9 * * 1"
INVALID_EXPR = "bad expression"


def test_build_report_valid_expression():
    results = build_report([VALID_EXPR])
    assert len(results) == 1
    assert results[0]["valid"] is True


def test_build_report_invalid_expression():
    results = build_report([INVALID_EXPR])
    assert results[0]["valid"] is False
    assert results[0]["description"] is None
    assert results[0]["next_runs"] == []


def test_build_report_has_description():
    results = build_report([VALID_EXPR])
    assert isinstance(results[0]["description"], str)
    assert len(results[0]["description"]) > 0


def test_build_report_has_next_runs():
    results = build_report([VALID_EXPR], count=3)
    assert len(results[0]["next_runs"]) == 3


def test_build_report_next_run_format():
    results = build_report([VALID_EXPR], count=1)
    run = results[0]["next_runs"][0]
    # Should match YYYY-MM-DD HH:MM
    assert len(run) == 16
    assert run[4] == "-"
    assert run[13] == ":"


def test_build_report_hints_list():
    results = build_report([VALID_EXPR])
    assert isinstance(results[0]["hints"], list)


def test_build_report_every_minute_has_hint():
    results = build_report(["* * * * *"])
    assert any("every minute" in h.lower() or len(h) > 0 for h in results[0]["hints"])


def test_build_report_multiple_expressions():
    results = build_report([VALID_EXPR, INVALID_EXPR])
    assert len(results) == 2
    assert results[0]["valid"] is True
    assert results[1]["valid"] is False


def test_format_report_contains_expression():
    report = build_report([VALID_EXPR])
    text = format_report(report)
    assert VALID_EXPR in text


def test_format_report_invalid_shows_invalid():
    report = build_report([INVALID_EXPR])
    text = format_report(report)
    assert "INVALID" in text


def test_format_report_valid_shows_desc():
    report = build_report([VALID_EXPR])
    text = format_report(report)
    assert "Desc" in text
