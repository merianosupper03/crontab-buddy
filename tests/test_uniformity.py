"""Tests for crontab_buddy.uniformity."""

import pytest
from crontab_buddy.uniformity import (
    assess_uniformity,
    batch_uniformity,
    UniformityResult,
    _firing_minutes,
)
from crontab_buddy.parser import CronExpression


def test_returns_uniformity_result():
    result = assess_uniformity("* * * * *")
    assert isinstance(result, UniformityResult)


def test_every_minute_is_excellent():
    result = assess_uniformity("* * * * *")
    assert result.grade == "excellent"
    assert result.score >= 0.99


def test_every_minute_has_no_error():
    result = assess_uniformity("* * * * *")
    assert result.error is None


def test_single_firing_per_day_is_clustered():
    result = assess_uniformity("0 9 * * *")
    # Only one firing per day means no intervals -> clustered
    assert result.grade == "clustered"
    assert result.score == 0.0


def test_two_firings_same_gap_is_excellent():
    # Fires at 00:00 and 12:00 every day — equal intervals
    result = assess_uniformity("0 0,12 * * *")
    assert result.score >= 0.95
    assert result.grade in ("excellent", "good")


def test_step_every_15_minutes_is_uniform():
    result = assess_uniformity("*/15 * * * *")
    assert result.score >= 0.95
    assert result.grade == "excellent"


def test_invalid_expression_returns_error():
    result = assess_uniformity("not a cron")
    assert result.error is not None
    assert result.score == 0.0
    assert result.grade == "clustered"


def test_invalid_expression_intervals_empty():
    result = assess_uniformity("99 99 * * *")
    assert result.error is not None
    assert result.intervals == []


def test_batch_returns_list():
    results = batch_uniformity(["* * * * *", "0 9 * * *"])
    assert len(results) == 2
    assert all(isinstance(r, UniformityResult) for r in results)


def test_batch_mixed_valid_invalid():
    results = batch_uniformity(["* * * * *", "bad expr"])
    assert results[0].error is None
    assert results[1].error is not None


def test_score_between_zero_and_one():
    for expr in ["*/5 * * * *", "0 */3 * * *", "30 6,18 * * *"]:
        r = assess_uniformity(expr)
        if r.error is None:
            assert 0.0 <= r.score <= 1.0


def test_firing_minutes_wildcard():
    expr = CronExpression("* * * * *")
    mins = _firing_minutes(expr)
    assert len(mins) == 1440
    assert mins[0] == 0
    assert mins[-1] == 1439


def test_firing_minutes_specific():
    expr = CronExpression("0 9 * * *")
    mins = _firing_minutes(expr)
    assert mins == [540]  # 9 * 60 + 0


def test_str_no_error():
    r = assess_uniformity("*/30 * * * *")
    s = str(r)
    assert "score=" in s
    assert "grade=" in s


def test_str_with_error():
    r = assess_uniformity("bad")
    s = str(r)
    assert "error=" in s
