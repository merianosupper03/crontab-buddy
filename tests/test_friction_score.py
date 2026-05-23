"""Tests for crontab_buddy.friction_score."""

import pytest
from crontab_buddy.friction_score import (
    compute_friction_score,
    FrictionScoreResult,
    _field_friction_score,
    _grade,
)


def test_returns_friction_score_result():
    r = compute_friction_score("0 9 * * 1")
    assert isinstance(r, FrictionScoreResult)


def test_invalid_expression_has_error():
    r = compute_friction_score("not valid")
    assert r.error is not None
    assert r.score == 1.0
    assert r.grade == "impenetrable"


def test_all_wildcards_is_smooth():
    r = compute_friction_score("* * * * *")
    assert r.grade in ("smooth", "manageable")
    assert r.score < 0.2


def test_all_exact_values_is_manageable_or_higher():
    r = compute_friction_score("0 9 1 1 1")
    assert r.score >= 0.0  # exact values are low friction
    assert r.grade in ("smooth", "manageable", "moderate")


def test_scores_dict_has_five_keys():
    r = compute_friction_score("*/5 * * * *")
    assert set(r.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_list_fields_raise_score():
    r_plain = compute_friction_score("0 9 * * *")
    r_list = compute_friction_score("0,15,30,45 9 * * *")
    assert r_list.score > r_plain.score


def test_step_expression_scores_above_wildcard():
    r_wild = compute_friction_score("* * * * *")
    r_step = compute_friction_score("*/1 * * * *")
    assert r_step.score >= r_wild.score


def test_field_friction_wildcard_is_zero():
    assert _field_friction_score("*") == 0.0


def test_field_friction_plain_integer_is_low():
    assert _field_friction_score("5") < 0.1


def test_field_friction_range_is_moderate():
    assert 0.1 < _field_friction_score("1-5") < 0.6


def test_field_friction_list_grows_with_length():
    s2 = _field_friction_score("1,2")
    s5 = _field_friction_score("1,2,3,4,5")
    assert s5 > s2


def test_grade_smooth():
    assert _grade(0.05) == "smooth"


def test_grade_manageable():
    assert _grade(0.25) == "manageable"


def test_grade_moderate():
    assert _grade(0.45) == "moderate"


def test_grade_dense():
    assert _grade(0.65) == "dense"


def test_grade_impenetrable():
    assert _grade(0.90) == "impenetrable"


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 0 * * *", "*/15 * * * *", "0,30 9-17 * * 1-5"]:
        r = compute_friction_score(expr)
        assert 0.0 <= r.score <= 1.0


def test_str_contains_grade():
    r = compute_friction_score("0 9 * * *")
    assert r.grade in str(r)


def test_str_error_contains_error_text():
    r = compute_friction_score("bad")
    assert "error" in str(r).lower()
