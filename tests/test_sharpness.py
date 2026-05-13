"""Tests for crontab_buddy.sharpness."""

import pytest
from crontab_buddy.sharpness import (
    assess_sharpness,
    batch_sharpness,
    SharpnessResult,
    _field_sharpness,
    _grade,
)


def test_returns_sharpness_result():
    r = assess_sharpness("30 6 * * *")
    assert isinstance(r, SharpnessResult)


def test_invalid_expression_has_error():
    r = assess_sharpness("not valid")
    assert r.error is not None
    assert r.score == 0.0
    assert r.grade == "dull"


def test_all_wildcards_is_dull():
    r = assess_sharpness("* * * * *")
    assert r.score == 0.0
    assert r.grade == "dull"


def test_all_exact_values_is_razor_or_sharp():
    r = assess_sharpness("30 6 15 6 1")
    assert r.score > 0.8
    assert r.grade in ("razor", "sharp")


def test_scores_dict_has_five_keys():
    r = assess_sharpness("0 12 * * *")
    assert set(r.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_wildcard_field_sharpness_is_zero():
    assert _field_sharpness("*", 59) == 0.0


def test_plain_integer_field_sharpness_is_one():
    assert _field_sharpness("30", 59) == 1.0


def test_step_expression_sharpness():
    val = _field_sharpness("*/15", 59)
    assert 0.0 < val <= 1.0


def test_range_field_sharpness_between_zero_and_one():
    val = _field_sharpness("0-5", 23)
    assert 0.0 <= val <= 1.0


def test_list_field_sharpness_positive():
    val = _field_sharpness("1,2,3", 7)
    assert val > 0.0


def test_grade_boundaries():
    assert _grade(1.0) == "razor"
    assert _grade(0.85) == "razor"
    assert _grade(0.65) == "sharp"
    assert _grade(0.45) == "moderate"
    assert _grade(0.25) == "blunt"
    assert _grade(0.0)  == "dull"


def test_batch_sharpness_returns_list():
    results = batch_sharpness(["* * * * *", "0 12 * * *", "bad expr"])
    assert len(results) == 3
    assert all(isinstance(r, SharpnessResult) for r in results)


def test_batch_sharpness_invalid_has_error():
    results = batch_sharpness(["bad expr"])
    assert results[0].error is not None


def test_str_representation_no_error():
    r = assess_sharpness("0 0 * * *")
    s = str(r)
    assert "SharpnessResult" in s
    assert "score" in s


def test_str_representation_with_error():
    r = assess_sharpness("oops")
    s = str(r)
    assert "error" in s
