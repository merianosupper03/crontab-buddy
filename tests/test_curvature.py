"""Tests for crontab_buddy.curvature."""

import pytest
from crontab_buddy.curvature import assess_curvature, batch_curvature, CurvatureResult


def test_returns_curvature_result():
    result = assess_curvature("* * * * *")
    assert isinstance(result, CurvatureResult)


def test_invalid_expression_has_error():
    result = assess_curvature("bad expr")
    assert result.error is not None
    assert result.score == 0.0


def test_every_minute_is_flat():
    # Fires every minute every hour — no change between hours, so flat
    result = assess_curvature("* * * * *")
    assert result.grade == "flat"
    assert result.score == 0.0


def test_single_hour_has_high_curvature():
    # Fires every minute but only at hour 12 — sharp transition
    result = assess_curvature("* 12 * * *")
    assert result.score > 0.0
    assert result.grade in ("steep", "curved", "gradual", "gentle")


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 9 * * 1", "*/15 * * * *", "0 0,12 * * *"]:
        result = assess_curvature(expr)
        if not result.error:
            assert 0.0 <= result.score <= 1.0


def test_grade_is_string():
    result = assess_curvature("0 9 * * 1")
    assert isinstance(result.grade, str)
    assert result.grade in ("steep", "curved", "gradual", "gentle", "flat")


def test_hourly_expression_has_low_curvature():
    # Fires at minute 0 every hour — uniform across all hours
    result = assess_curvature("0 * * * *")
    assert result.grade == "flat"
    assert result.score == 0.0


def test_two_hour_window_has_curvature():
    result = assess_curvature("* 8-9 * * *")
    assert result.score > 0.0


def test_batch_returns_list():
    results = batch_curvature(["* * * * *", "0 9 * * 1", "bad"])
    assert len(results) == 3
    assert all(isinstance(r, CurvatureResult) for r in results)


def test_batch_invalid_has_error():
    results = batch_curvature(["bad expr"])
    assert results[0].error is not None


def test_str_with_error():
    result = assess_curvature("not valid")
    s = str(result)
    assert "error" in s


def test_str_without_error():
    result = assess_curvature("* * * * *")
    s = str(result)
    assert "score" in s
    assert "grade" in s
