"""Tests for crontab_buddy.volatility."""

import pytest
from crontab_buddy.volatility import (
    assess_volatility,
    batch_volatility,
    VolatilityResult,
    VOLATILITY_THRESHOLDS,
)


def test_assess_returns_volatility_result():
    result = assess_volatility("* * * * *")
    assert isinstance(result, VolatilityResult)


def test_every_minute_is_extreme():
    result = assess_volatility("* * * * *")
    assert result.valid
    assert result.level == "extreme"


def test_every_minute_score_near_one():
    result = assess_volatility("* * * * *")
    assert result.score > 0.9


def test_daily_is_low_volatility():
    result = assess_volatility("0 9 * * *")
    assert result.valid
    assert result.level in ("low", "moderate", "very_low", "stable")


def test_weekly_is_very_low_or_stable():
    result = assess_volatility("0 0 * * 0")
    assert result.valid
    assert result.level in ("very_low", "stable", "low")


def test_invalid_expression_not_valid():
    result = assess_volatility("not a cron")
    assert not result.valid
    assert result.error != ""


def test_invalid_expression_level_is_unknown():
    result = assess_volatility("99 99 99 99 99")
    assert not result.valid
    assert result.level == "unknown"


def test_interval_seconds_populated():
    result = assess_volatility("* * * * *")
    assert result.interval_seconds == 60


def test_description_is_string():
    result = assess_volatility("0 * * * *")
    assert isinstance(result.description, str)
    assert len(result.description) > 0


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 * * * *", "0 9 * * *", "0 0 * * 0"]:
        result = assess_volatility(expr)
        if result.valid:
            assert 0.0 <= result.score <= 1.0


def test_batch_volatility_returns_list():
    results = batch_volatility(["* * * * *", "0 9 * * *"])
    assert len(results) == 2


def test_batch_volatility_all_results():
    results = batch_volatility(["* * * * *", "invalid"])
    assert results[0].valid
    assert not results[1].valid


def test_str_valid_result():
    result = assess_volatility("* * * * *")
    s = str(result)
    assert "extreme" in s or "very_high" in s or "high" in s


def test_str_invalid_result():
    result = assess_volatility("bad expr")
    s = str(result)
    assert "invalid" in s.lower()


def test_thresholds_are_sorted():
    thresholds = [t for t, _ in VOLATILITY_THRESHOLDS]
    assert thresholds == sorted(thresholds)
