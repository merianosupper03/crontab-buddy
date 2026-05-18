"""Tests for crontab_buddy.intensity."""

import pytest
from crontab_buddy.intensity import assess_intensity, batch_intensity, IntensityResult


def test_returns_intensity_result():
    result = assess_intensity("* * * * *")
    assert isinstance(result, IntensityResult)


def test_invalid_expression_has_error():
    result = assess_intensity("not valid")
    assert result.error is not None
    assert result.score == 0.0


def test_every_minute_is_overwhelming():
    result = assess_intensity("* * * * *")
    assert result.grade == "overwhelming"


def test_every_minute_runs_1440_per_day():
    result = assess_intensity("* * * * *")
    assert result.runs_per_day == 1440


def test_every_minute_score_near_one():
    result = assess_intensity("* * * * *")
    assert result.score == pytest.approx(1.0, abs=0.01)


def test_hourly_runs_24_per_day():
    result = assess_intensity("0 * * * *")
    assert result.runs_per_day == 24


def test_daily_runs_1_per_day():
    result = assess_intensity("0 9 * * *")
    assert result.runs_per_day == 1


def test_daily_grade_is_negligible():
    result = assess_intensity("0 9 * * *")
    assert result.grade == "negligible"


def test_step_minute_runs_correct_count():
    # */15 fires at 0,15,30,45 => 4 per hour, 24 hours = 96
    result = assess_intensity("*/15 * * * *")
    assert result.runs_per_day == 96


def test_specific_hour_reduces_runs():
    result = assess_intensity("* 9 * * *")
    assert result.runs_per_day == 60


def test_list_minutes_counted_correctly():
    result = assess_intensity("0,30 * * * *")
    assert result.runs_per_day == 48


def test_range_minutes_counted_correctly():
    result = assess_intensity("0-4 * * * *")
    assert result.runs_per_day == 5 * 24


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 * * * *", "0 9 * * *", "*/5 * * * *"]:
        r = assess_intensity(expr)
        assert 0.0 <= r.score <= 1.0


def test_str_contains_grade():
    result = assess_intensity("0 9 * * *")
    assert result.grade in str(result)


def test_batch_returns_list():
    results = batch_intensity(["* * * * *", "0 9 * * *"])
    assert len(results) == 2
    assert all(isinstance(r, IntensityResult) for r in results)
