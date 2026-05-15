"""Tests for crontab_buddy.monotony."""

import pytest
from crontab_buddy.monotony import (
    assess_monotony,
    batch_monotony,
    MonotonyResult,
    _field_monotony,
    _grade,
)


def test_returns_monotony_result():
    result = assess_monotony("0 9 * * 1")
    assert isinstance(result, MonotonyResult)


def test_invalid_expression_has_error():
    result = assess_monotony("not valid")
    assert result.error is not None
    assert result.score == 0.0


def test_all_wildcards_is_numbing_or_repetitive():
    result = assess_monotony("* * * * *")
    assert result.score == 1.0
    assert result.grade in ("numbing",)


def test_single_exact_time_is_high_monotony():
    result = assess_monotony("0 9 * * *")
    assert result.score >= 0.7


def test_list_fields_reduce_monotony():
    result_list = assess_monotony("0,15,30,45 * * * *")
    result_plain = assess_monotony("0 * * * *")
    assert result_list.score < result_plain.score


def test_step_expression_reduces_monotony():
    result_step = assess_monotony("*/5 * * * *")
    result_wild = assess_monotony("* * * * *")
    assert result_step.score < result_wild.score


def test_scores_dict_has_five_keys():
    result = assess_monotony("0 12 * * *")
    assert set(result.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_field_monotony_wildcard_is_one():
    assert _field_monotony("*") == 1.0


def test_field_monotony_plain_integer_is_one():
    assert _field_monotony("5") == 1.0


def test_field_monotony_list_decreases():
    score = _field_monotony("1,2,3,4")
    assert score < 1.0
    assert score >= 0.0


def test_field_monotony_range_decreases():
    score = _field_monotony("0-10")
    assert score < 1.0


def test_field_monotony_step_between_zero_and_one():
    score = _field_monotony("*/15")
    assert 0.0 <= score <= 1.0


def test_grade_numbing():
    assert _grade(0.95) == "numbing"


def test_grade_repetitive():
    assert _grade(0.75) == "repetitive"


def test_grade_routine():
    assert _grade(0.55) == "routine"


def test_grade_varied():
    assert _grade(0.35) == "varied"


def test_grade_dynamic():
    assert _grade(0.1) == "dynamic"


def test_batch_monotony_returns_list():
    results = batch_monotony(["* * * * *", "0 9 * * 1", "bad expr"])
    assert len(results) == 3
    assert all(isinstance(r, MonotonyResult) for r in results)


def test_batch_monotony_invalid_has_error():
    results = batch_monotony(["bad"])
    assert results[0].error is not None


def test_str_with_error():
    result = assess_monotony("nope")
    assert "error" in str(result).lower()


def test_str_without_error():
    result = assess_monotony("0 0 * * *")
    s = str(result)
    assert "score" in s
    assert "grade" in s
