"""Tests for crontab_buddy.fading."""

import pytest
from crontab_buddy.fading import assess_fading, batch_fading, FadingResult


def test_returns_fading_result():
    result = assess_fading("* * * * *")
    assert isinstance(result, FadingResult)


def test_invalid_expression_has_error():
    result = assess_fading("not a cron")
    assert result.error is not None
    assert result.score == 0.0
    assert result.grade == "F"


def test_every_minute_is_instant():
    result = assess_fading("* * * * *")
    assert result.error is None
    assert result.label == "instant"


def test_every_minute_score_near_one():
    result = assess_fading("* * * * *")
    assert result.score >= 0.9


def test_hourly_is_rapid_or_moderate():
    result = assess_fading("0 * * * *")
    assert result.error is None
    assert result.label in ("rapid", "moderate", "instant")


def test_daily_is_moderate_or_gradual():
    result = assess_fading("0 9 * * *")
    assert result.error is None
    assert result.label in ("moderate", "gradual", "slow")


def test_weekly_is_gradual_or_slow():
    result = assess_fading("0 9 * * 1")
    assert result.error is None
    assert result.label in ("gradual", "slow", "glacial")


def test_grade_a_for_high_score():
    result = assess_fading("* * * * *")
    assert result.grade == "A"


def test_interval_seconds_present_for_valid():
    result = assess_fading("*/5 * * * *")
    assert result.interval_seconds is not None
    assert result.interval_seconds > 0


def test_interval_seconds_none_for_invalid():
    result = assess_fading("bad expr")
    assert result.interval_seconds is None


def test_str_contains_label_for_valid():
    result = assess_fading("* * * * *")
    assert "instant" in str(result)


def test_str_contains_error_for_invalid():
    result = assess_fading("bad")
    assert "error" in str(result).lower()


def test_batch_fading_returns_list():
    results = batch_fading(["* * * * *", "0 9 * * *"])
    assert isinstance(results, list)
    assert len(results) == 2


def test_batch_fading_handles_invalid():
    results = batch_fading(["* * * * *", "not valid"])
    assert results[0].error is None
    assert results[1].error is not None


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 * * * *", "0 9 * * *", "0 9 * * 1"]:
        r = assess_fading(expr)
        if r.error is None:
            assert 0.0 <= r.score <= 1.0
