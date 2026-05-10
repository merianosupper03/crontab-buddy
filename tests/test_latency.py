"""Tests for crontab_buddy.latency."""

import pytest
from crontab_buddy.latency import assess_latency, batch_latency, LatencyResult


def test_returns_latency_result():
    result = assess_latency("* * * * *")
    assert isinstance(result, LatencyResult)


def test_every_minute_interval_is_60():
    result = assess_latency("* * * * *")
    assert result.error is None
    assert result.interval_seconds == 60.0


def test_every_minute_grade_is_instant():
    result = assess_latency("* * * * *")
    assert result.grade == "instant"


def test_every_five_minutes_is_rapid():
    result = assess_latency("*/5 * * * *")
    assert result.error is None
    assert result.grade == "rapid"


def test_hourly_is_regular_or_frequent():
    result = assess_latency("0 * * * *")
    assert result.error is None
    assert result.grade in ("regular", "frequent")


def test_daily_is_infrequent():
    result = assess_latency("0 9 * * *")
    assert result.error is None
    assert result.grade == "infrequent"


def test_weekly_is_rare():
    result = assess_latency("0 9 * * 1")
    assert result.error is None
    assert result.grade == "rare"


def test_invalid_expression_has_error():
    result = assess_latency("not a cron")
    assert result.error is not None
    assert result.interval_seconds is None


def test_invalid_expression_grade_is_unknown():
    result = assess_latency("99 99 99 99 99")
    assert result.grade == "unknown"


def test_expression_stored_on_result():
    expr = "30 6 * * *"
    result = assess_latency(expr)
    assert result.expression == expr


def test_str_contains_grade():
    result = assess_latency("0 9 * * *")
    assert result.grade in str(result)


def test_str_contains_error_when_invalid():
    result = assess_latency("bad")
    assert "error" in str(result).lower()


def test_batch_returns_list():
    results = batch_latency(["* * * * *", "0 9 * * *"])
    assert isinstance(results, list)
    assert len(results) == 2


def test_batch_preserves_order():
    exprs = ["* * * * *", "0 9 * * *", "0 9 * * 1"]
    results = batch_latency(exprs)
    for r, e in zip(results, exprs):
        assert r.expression == e


def test_batch_handles_invalid_entries():
    results = batch_latency(["* * * * *", "not valid"])
    assert results[0].error is None
    assert results[1].error is not None
