"""Tests for crontab_buddy.cadence_score."""

import pytest

from crontab_buddy.cadence_score import compute_cadence_score, CadenceScoreResult


def test_returns_cadence_score_result():
    result = compute_cadence_score("0 9 * * 1")
    assert isinstance(result, CadenceScoreResult)


def test_invalid_expression_has_error():
    result = compute_cadence_score("not valid")
    assert result.error is not None
    assert result.grade == "F"
    assert result.score == 0.0


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 9 * * 1", "30 6 * * *", "0 0 1 1 *"]:
        result = compute_cadence_score(expr)
        assert 0.0 <= result.score <= 1.0, f"Out of range for {expr!r}"


def test_every_minute_has_low_score():
    result = compute_cadence_score("* * * * *")
    assert result.score < 0.5


def test_weekly_expression_has_higher_score_than_every_minute():
    weekly = compute_cadence_score("0 9 * * 1")
    every_min = compute_cadence_score("* * * * *")
    assert weekly.score > every_min.score


def test_grade_is_letter():
    result = compute_cadence_score("0 9 * * 1")
    assert result.grade in {"A", "B", "C", "D", "F"}


def test_interval_seconds_populated_for_valid_expression():
    result = compute_cadence_score("0 * * * *")
    assert result.interval_seconds is not None
    assert result.interval_seconds > 0


def test_interval_seconds_none_for_invalid():
    result = compute_cadence_score("bad expr here")
    assert result.interval_seconds is None


def test_complexity_level_is_string():
    result = compute_cadence_score("0 9 * * 1")
    assert isinstance(result.complexity_level, str)
    assert len(result.complexity_level) > 0


def test_entropy_level_is_string():
    result = compute_cadence_score("0 9 * * 1")
    assert isinstance(result.entropy_level, str)


def test_regularity_grade_is_string():
    result = compute_cadence_score("0 9 * * 1")
    assert isinstance(result.regularity_grade, str)


def test_str_representation_no_error():
    result = compute_cadence_score("0 9 * * 1")
    s = str(result)
    assert "CadenceScore" in s
    assert "score=" in s


def test_str_representation_with_error():
    result = compute_cadence_score("bad")
    s = str(result)
    assert "ERROR" in s


def test_no_error_field_for_valid():
    result = compute_cadence_score("30 6 * * *")
    assert result.error is None
