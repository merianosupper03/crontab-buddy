"""Tests for crontab_buddy.pulse."""
import pytest
from crontab_buddy.pulse import assess_pulse, batch_pulse, PulseResult


def test_returns_pulse_result():
    result = assess_pulse("* * * * *")
    assert isinstance(result, PulseResult)


def test_every_minute_is_racing():
    result = assess_pulse("* * * * *")
    assert result.level == "racing"


def test_every_minute_score_near_one():
    result = assess_pulse("* * * * *")
    assert result.score >= 0.99


def test_hourly_is_steady_or_calm():
    result = assess_pulse("0 * * * *")
    assert result.level in ("steady", "calm", "rapid")


def test_daily_is_quiet_or_calm():
    result = assess_pulse("0 9 * * *")
    assert result.level in ("quiet", "calm")


def test_weekly_is_dormant():
    result = assess_pulse("0 9 * * 1")
    assert result.level in ("dormant", "quiet")


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 * * * *", "0 9 * * *", "0 9 * * 1"]:
        r = assess_pulse(expr)
        assert 0.0 <= r.score <= 1.0


def test_invalid_expression_returns_error():
    result = assess_pulse("not a cron")
    assert result.error is not None
    assert result.score == 0.0


def test_invalid_expression_level_unknown():
    result = assess_pulse("99 99 99 99 99")
    assert result.level == "unknown"


def test_interval_seconds_populated_for_valid():
    result = assess_pulse("*/5 * * * *")
    assert result.interval_seconds is not None
    assert result.interval_seconds > 0


def test_interval_seconds_none_for_invalid():
    result = assess_pulse("bad expression here")
    assert result.interval_seconds is None


def test_faster_expression_has_higher_score():
    fast = assess_pulse("* * * * *")
    slow = assess_pulse("0 0 * * 0")
    assert fast.score > slow.score


def test_str_no_error():
    result = assess_pulse("0 * * * *")
    s = str(result)
    assert "PulseResult" in s
    assert "error" not in s


def test_str_with_error():
    result = assess_pulse("bad")
    s = str(result)
    assert "error" in s


def test_batch_pulse_returns_list():
    results = batch_pulse(["* * * * *", "0 9 * * *"])
    assert len(results) == 2
    assert all(isinstance(r, PulseResult) for r in results)


def test_batch_pulse_handles_invalid():
    results = batch_pulse(["* * * * *", "bad expr"])
    assert results[0].error is None
    assert results[1].error is not None
