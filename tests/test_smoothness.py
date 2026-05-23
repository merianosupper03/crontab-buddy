"""Tests for crontab_buddy.smoothness."""

import pytest
from crontab_buddy.smoothness import (
    assess_smoothness,
    batch_smoothness,
    SmoothnessResult,
    _firing_minutes,
    _grade,
)
from crontab_buddy.parser import CronExpression


def test_returns_smoothness_result():
    result = assess_smoothness("* * * * *")
    assert isinstance(result, SmoothnessResult)


def test_invalid_expression_has_error():
    result = assess_smoothness("invalid")
    assert result.error is not None
    assert result.score == 0.0
    assert result.grade == "jagged"


def test_every_minute_is_silky_or_smooth():
    result = assess_smoothness("* * * * *")
    assert result.error is None
    assert result.grade in ("silky", "smooth")


def test_every_minute_fires_60_times():
    result = assess_smoothness("* * * * *")
    assert len(result.firing_minutes) == 60


def test_every_minute_score_near_one():
    result = assess_smoothness("* * * * *")
    assert result.score >= 0.95


def test_single_firing_per_hour_has_no_intervals():
    result = assess_smoothness("0 * * * *")
    assert result.intervals == []


def test_single_firing_score_is_zero():
    result = assess_smoothness("0 * * * *")
    assert result.score == 0.0


def test_every_15_minutes_is_smooth():
    result = assess_smoothness("*/15 * * * *")
    assert result.error is None
    assert result.grade in ("silky", "smooth")


def test_every_15_minutes_has_4_firings():
    result = assess_smoothness("*/15 * * * *")
    assert len(result.firing_minutes) == 4


def test_list_minutes_clustered_is_rough_or_jagged():
    # 0,1,2,3 — clustered at start
    result = assess_smoothness("0,1,2,3 * * * *")
    assert result.score < 0.5


def test_grade_silky():
    assert _grade(0.95) == "silky"


def test_grade_smooth():
    assert _grade(0.80) == "smooth"


def test_grade_moderate():
    assert _grade(0.60) == "moderate"


def test_grade_rough():
    assert _grade(0.40) == "rough"


def test_grade_jagged():
    assert _grade(0.10) == "jagged"


def test_firing_minutes_wildcard():
    expr = CronExpression("* * * * *")
    mins = _firing_minutes(expr)
    assert mins == list(range(60))


def test_firing_minutes_step():
    expr = CronExpression("*/10 * * * *")
    mins = _firing_minutes(expr)
    assert mins == [0, 10, 20, 30, 40, 50]


def test_firing_minutes_range():
    expr = CronExpression("5-8 * * * *")
    mins = _firing_minutes(expr)
    assert mins == [5, 6, 7, 8]


def test_batch_smoothness_returns_list():
    results = batch_smoothness(["* * * * *", "0 * * * *"])
    assert len(results) == 2
    assert all(isinstance(r, SmoothnessResult) for r in results)


def test_str_with_error():
    result = assess_smoothness("bad")
    assert "error" in str(result).lower()


def test_str_without_error():
    result = assess_smoothness("* * * * *")
    s = str(result)
    assert "score" in s
    assert "grade" in s
