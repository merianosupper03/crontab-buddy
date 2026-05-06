"""Tests for crontab_buddy.stability."""

import pytest
from unittest.mock import patch
from crontab_buddy.stability import assess_stability, StabilityResult, STABILITY_LEVELS


def test_returns_stability_result():
    result = assess_stability("0 * * * *")
    assert isinstance(result, StabilityResult)


def test_every_minute_is_unstable():
    result = assess_stability("* * * * *")
    assert result.level in ("unstable", "fragile")
    assert result.score < 0.3


def test_hourly_is_at_least_moderate():
    result = assess_stability("0 * * * *")
    assert result.score >= 0.4


def test_daily_is_stable_or_better():
    result = assess_stability("0 9 * * *")
    assert result.level in ("stable", "rock-solid")
    assert result.score >= 0.65


def test_weekly_is_rock_solid():
    result = assess_stability("0 9 * * 1")
    assert result.level == "rock-solid"
    assert result.score >= 0.85


def test_invalid_expression_is_unstable():
    result = assess_stability("not a cron")
    assert result.level == "unstable"
    assert result.score == 0.0
    assert result.interval_seconds is None
    assert any("parse error" in n for n in result.notes)


def test_all_wildcards_note_present():
    result = assess_stability("* * * * *")
    assert any("wildcard" in n or "every minute" in n for n in result.notes)


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 * * * *", "0 9 * * *", "0 9 1 * *", "0 9 * * 1"]:
        result = assess_stability(expr)
        assert 0.0 <= result.score <= 1.0


def test_level_is_known_value():
    for expr in ["* * * * *", "0 * * * *", "0 9 * * 1"]:
        result = assess_stability(expr)
        assert result.level in STABILITY_LEVELS


def test_interval_seconds_populated_for_valid():
    result = assess_stability("0 * * * *")
    assert result.interval_seconds is not None
    assert result.interval_seconds > 0


def test_many_list_fields_reduce_score():
    # expression with several list fields
    result_simple = assess_stability("0 9 * * *")
    result_lists = assess_stability("0,30 9,12 * * 1,3,5")
    assert result_lists.score <= result_simple.score


def test_str_representation():
    result = assess_stability("0 9 * * *")
    s = str(result)
    assert "StabilityResult" in s
    assert "0 9 * * *" in s
