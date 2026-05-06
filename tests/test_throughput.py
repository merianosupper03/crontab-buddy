"""Tests for crontab_buddy.throughput."""

import pytest
from crontab_buddy.throughput import (
    estimate_runs,
    throughput_report,
    format_throughput,
    WINDOWS,
)


def test_windows_contains_expected_keys():
    for key in ("1h", "6h", "12h", "24h", "7d", "30d"):
        assert key in WINDOWS


def test_estimate_runs_every_minute_24h():
    result = estimate_runs("* * * * *", WINDOWS["24h"])
    assert result == 1440  # 86400 / 60


def test_estimate_runs_every_hour_24h():
    result = estimate_runs("0 * * * *", WINDOWS["24h"])
    assert result == 24


def test_estimate_runs_daily_24h():
    result = estimate_runs("0 0 * * *", WINDOWS["24h"])
    assert result == 1


def test_estimate_runs_step_minute():
    # */5 * * * * => every 5 minutes => 288 times per day
    result = estimate_runs("*/5 * * * *", WINDOWS["24h"])
    assert result == 288


def test_estimate_runs_step_hour():
    # 0 */2 * * * => every 2 hours => 12 times per day
    result = estimate_runs("0 */2 * * *", WINDOWS["24h"])
    assert result == 12


def test_estimate_runs_invalid_expression_returns_none():
    result = estimate_runs("not a cron", WINDOWS["24h"])
    assert result is None


def test_estimate_runs_too_few_fields_returns_none():
    result = estimate_runs("* * *", WINDOWS["24h"])
    assert result is None


def test_throughput_report_returns_list():
    report = throughput_report(["* * * * *", "0 0 * * *"], "24h")
    assert isinstance(report, list)
    assert len(report) == 2


def test_throughput_report_valid_flag():
    report = throughput_report(["* * * * *", "bad expr"], "24h")
    assert report[0]["valid"] is True
    assert report[1]["valid"] is False


def test_throughput_report_window_label():
    report = throughput_report(["* * * * *"], "1h")
    assert report[0]["window"] == "1h"


def test_throughput_report_expression_preserved():
    expr = "0 12 * * 1"
    report = throughput_report([expr], "7d")
    assert report[0]["expression"] == expr


def test_format_throughput_contains_expression():
    report = throughput_report(["* * * * *"], "24h")
    output = format_throughput(report)
    assert "* * * * *" in output


def test_format_throughput_invalid_shows_invalid():
    report = throughput_report(["bad"], "24h")
    output = format_throughput(report)
    assert "INVALID" in output


def test_format_throughput_empty_list():
    output = format_throughput([])
    assert "no expressions" in output
