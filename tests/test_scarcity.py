"""Tests for crontab_buddy.scarcity."""
import pytest
from crontab_buddy.scarcity import assess_scarcity, batch_scarcity, ScarcityResult


def test_returns_scarcity_result():
    result = assess_scarcity("* * * * *")
    assert isinstance(result, ScarcityResult)


def test_invalid_expression_has_error():
    result = assess_scarcity("bad expr")
    assert result.error is not None
    assert result.score == 0.0
    assert result.grade == "elusive"


def test_every_minute_fires_1440():
    result = assess_scarcity("* * * * *")
    assert result.firing_minutes == 1440
    assert result.error is None


def test_every_minute_score_is_one():
    result = assess_scarcity("* * * * *")
    assert abs(result.score - 1.0) < 1e-6


def test_every_minute_grade_is_abundant():
    result = assess_scarcity("* * * * *")
    assert result.grade == "abundant"


def test_single_exact_time_fires_once():
    result = assess_scarcity("30 9 * * *")
    assert result.firing_minutes == 1


def test_single_exact_time_is_rare_or_elusive():
    result = assess_scarcity("30 9 * * *")
    assert result.grade in ("elusive", "rare")


def test_hourly_fires_24():
    result = assess_scarcity("0 * * * *")
    assert result.firing_minutes == 24


def test_hourly_score():
    result = assess_scarcity("0 * * * *")
    expected = 24 / 1440
    assert abs(result.score - expected) < 1e-4


def test_step_every_15_minutes():
    result = assess_scarcity("*/15 * * * *")
    # 4 minutes * 24 hours = 96
    assert result.firing_minutes == 96


def test_step_every_15_minutes_grade_is_plentiful_or_moderate():
    result = assess_scarcity("*/15 * * * *")
    assert result.grade in ("plentiful", "moderate", "abundant")


def test_weekly_expression_is_scarce_or_rarer():
    # fires once per week but cron doesn't know weeks; per-day it still fires daily
    result = assess_scarcity("0 9 * * 1")
    # dow field doesn't affect minute/hour counting in our model
    assert result.firing_minutes == 1
    assert result.grade in ("elusive", "rare")


def test_scores_dict_has_no_error_for_valid():
    result = assess_scarcity("*/5 */2 * * *")
    assert result.error is None


def test_batch_scarcity_returns_list():
    results = batch_scarcity(["* * * * *", "0 9 * * *"])
    assert isinstance(results, list)
    assert len(results) == 2


def test_batch_scarcity_first_is_abundant():
    results = batch_scarcity(["* * * * *", "0 9 * * *"])
    assert results[0].grade == "abundant"


def test_str_with_error():
    result = assess_scarcity("not valid")
    s = str(result)
    assert "error" in s.lower()


def test_str_without_error():
    result = assess_scarcity("* * * * *")
    s = str(result)
    assert "abundant" in s
