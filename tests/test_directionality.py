"""Tests for crontab_buddy.directionality."""
import pytest
from crontab_buddy.directionality import (
    assess_directionality,
    batch_directionality,
    DirectionalityResult,
)


def test_returns_directionality_result():
    result = assess_directionality("0 9 * * *")
    assert isinstance(result, DirectionalityResult)


def test_invalid_expression_has_error():
    result = assess_directionality("bad expr")
    assert result.error is not None
    assert result.dominant_period is None


def test_morning_expression_dominant():
    # fires every minute during hours 6-11
    result = assess_directionality("* 6-11 * * *")
    assert result.dominant_period == "morning"
    assert result.error is None


def test_night_expression_dominant():
    result = assess_directionality("0 1 * * *")
    assert result.dominant_period == "night"


def test_afternoon_expression_dominant():
    result = assess_directionality("30 14 * * *")
    assert result.dominant_period == "afternoon"


def test_evening_expression_dominant():
    result = assess_directionality("0 20 * * *")
    assert result.dominant_period == "evening"


def test_all_hours_wildcard_is_neutral_or_mixed():
    result = assess_directionality("* * * * *")
    assert result.grade in ("neutral", "mixed")
    assert result.dominant_period is not None


def test_scores_sum_to_one():
    result = assess_directionality("0 * * * *")
    assert result.error is None
    total = sum(result.scores.values())
    assert abs(total - 1.0) < 1e-6


def test_scores_dict_has_four_keys():
    result = assess_directionality("0 9 * * *")
    assert set(result.scores.keys()) == {"night", "morning", "afternoon", "evening"}


def test_grade_dominant_for_single_period():
    # only fires at hour 10 (morning)
    result = assess_directionality("0 10 * * *")
    assert result.grade == "dominant"
    assert result.dominant_period == "morning"


def test_batch_returns_list():
    results = batch_directionality(["0 9 * * *", "0 21 * * *"])
    assert len(results) == 2
    assert all(isinstance(r, DirectionalityResult) for r in results)


def test_batch_invalid_included():
    results = batch_directionality(["0 9 * * *", "not valid"])
    assert results[1].error is not None


def test_str_no_error():
    result = assess_directionality("0 9 * * *")
    s = str(result)
    assert "dominant" in s or "leaning" in s or "mixed" in s or "neutral" in s


def test_str_with_error():
    result = assess_directionality("bad")
    s = str(result)
    assert "error" in s.lower()
