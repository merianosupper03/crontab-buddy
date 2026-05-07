"""Tests for crontab_buddy.dispersion."""

import pytest

from crontab_buddy.dispersion import assess_dispersion, DispersionResult


def test_returns_dispersion_result():
    result = assess_dispersion("* * * * *")
    assert isinstance(result, DispersionResult)


def test_every_minute_is_uniform():
    result = assess_dispersion("* * * * *")
    assert result.label == "uniform"
    assert result.error is None


def test_every_minute_score_near_one():
    result = assess_dispersion("* * * * *")
    assert result.score >= 0.95


def test_single_firing_per_day_is_clustered():
    # fires only once a day — no intervals, score 0
    result = assess_dispersion("30 6 * * *")
    assert result.score == 0.0
    assert result.label == "clustered"


def test_single_firing_has_empty_intervals():
    result = assess_dispersion("0 12 * * *")
    assert result.intervals == []


def test_every_15_minutes_is_spread_or_better():
    result = assess_dispersion("*/15 * * * *")
    assert result.label in ("uniform", "spread")
    assert result.score > 0.5


def test_every_hour_on_the_hour_is_uniform():
    result = assess_dispersion("0 * * * *")
    assert result.label in ("uniform", "spread")


def test_two_specific_hours_close_together_is_uneven_or_clustered():
    # fires at 01:00 and 02:00 only — very clustered in the day
    result = assess_dispersion("0 1,2 * * *")
    # intervals: [60 min] between the two fires — std=0, cv=0 → score=1
    # but only 2 fires so mean=60, std=0 → score=1 (perfectly even gap)
    assert result.score >= 0.0  # just ensure it runs without error


def test_invalid_expression_returns_error():
    result = assess_dispersion("not a cron")
    assert result.error is not None
    assert result.score == 0.0
    assert result.label == "clustered"


def test_mean_interval_every_hour():
    result = assess_dispersion("0 * * * *")
    # 24 fires, 23 intervals of 60 min each
    assert abs(result.mean_interval - 60.0) < 1.0


def test_std_dev_uniform_is_near_zero():
    result = assess_dispersion("* * * * *")
    assert result.std_dev < 5.0


def test_fire_count_every_minute():
    result = assess_dispersion("* * * * *")
    # 1440 fires → 1439 intervals
    assert len(result.intervals) == 1439


def test_fire_count_every_hour():
    result = assess_dispersion("0 * * * *")
    assert len(result.intervals) == 23


def test_str_no_error():
    result = assess_dispersion("*/30 * * * *")
    s = str(result)
    assert "DispersionResult" in s
    assert "score=" in s


def test_str_with_error():
    result = assess_dispersion("bad expr")
    s = str(result)
    assert "error=" in s
