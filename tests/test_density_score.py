"""Tests for crontab_buddy.density_score."""

import pytest

from crontab_buddy.density_score import (
    DensityScoreResult,
    compute_density_score,
    _grade,
)


def test_returns_density_score_result():
    result = compute_density_score("* * * * *")
    assert isinstance(result, DensityScoreResult)


def test_invalid_expression_has_error():
    result = compute_density_score("not a cron")
    assert result.error is not None
    assert result.score == 0.0
    assert result.fires_per_day == 0


def test_every_minute_fires_1440():
    result = compute_density_score("* * * * *")
    assert result.fires_per_day == 1440


def test_every_minute_score_is_one():
    result = compute_density_score("* * * * *")
    assert result.score == pytest.approx(1.0, abs=0.001)


def test_every_minute_grade_is_packed():
    result = compute_density_score("* * * * *")
    assert result.grade == "packed"


def test_hourly_fires_24():
    result = compute_density_score("0 * * * *")
    assert result.fires_per_day == 24


def test_hourly_score_is_low():
    result = compute_density_score("0 * * * *")
    expected = 24 / 1440
    assert result.score == pytest.approx(expected, abs=0.001)


def test_daily_fires_once():
    result = compute_density_score("0 9 * * *")
    assert result.fires_per_day == 1


def test_daily_score_is_very_low():
    result = compute_density_score("0 9 * * *")
    assert result.score < 0.01


def test_daily_grade_is_minimal():
    result = compute_density_score("0 9 * * *")
    assert result.grade == "minimal"


def test_step_every_5_minutes():
    result = compute_density_score("*/5 * * * *")
    assert result.fires_per_day == 288


def test_step_every_5_minutes_score():
    result = compute_density_score("*/5 * * * *")
    expected = 288 / 1440
    assert result.score == pytest.approx(expected, abs=0.001)


def test_grade_thresholds():
    assert _grade(0.95) == "packed"
    assert _grade(0.75) == "dense"
    assert _grade(0.55) == "moderate"
    assert _grade(0.35) == "sparse"
    assert _grade(0.1) == "minimal"


def test_str_with_error():
    result = compute_density_score("bad expr")
    s = str(result)
    assert "error" in s


def test_str_without_error():
    result = compute_density_score("0 9 * * *")
    s = str(result)
    assert "score=" in s
    assert "grade=" in s
    assert "fires/day=" in s
