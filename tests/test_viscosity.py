"""Tests for crontab_buddy.viscosity."""

import pytest
from crontab_buddy.viscosity import (
    assess_viscosity,
    batch_viscosity,
    ViscosityResult,
    _field_viscosity,
    _grade,
)


def test_returns_viscosity_result():
    result = assess_viscosity("* * * * *")
    assert isinstance(result, ViscosityResult)


def test_invalid_expression_has_error():
    result = assess_viscosity("bad expr")
    assert result.error is not None
    assert result.score == 0.0


def test_all_wildcards_is_free_flowing():
    result = assess_viscosity("* * * * *")
    assert result.error is None
    assert result.score == 0.0
    assert result.grade == "free-flowing"


def test_all_exact_values_is_rigid():
    result = assess_viscosity("30 14 5 6 1")
    assert result.error is None
    assert result.score >= 0.85
    assert result.grade == "rigid"


def test_scores_dict_has_five_keys():
    result = assess_viscosity("0 9 * * 1")
    assert result.error is None
    assert set(result.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_step_expression_is_fluid_or_moderate():
    result = assess_viscosity("*/15 * * * *")
    assert result.error is None
    assert result.grade in ("free-flowing", "fluid", "moderate")


def test_list_field_raises_score():
    result_list = assess_viscosity("1,2,3 * * * *")
    result_wild = assess_viscosity("* * * * *")
    assert result_list.score > result_wild.score


def test_range_field_moderate_viscosity():
    score = _field_viscosity("9-17")
    assert 0.4 <= score <= 0.75


def test_wildcard_field_is_zero():
    assert _field_viscosity("*") == 0.0


def test_exact_integer_field_is_one():
    assert _field_viscosity("42") == 1.0


def test_grade_rigid():
    assert _grade(0.9) == "rigid"


def test_grade_thick():
    assert _grade(0.7) == "thick"


def test_grade_moderate():
    assert _grade(0.5) == "moderate"


def test_grade_fluid():
    assert _grade(0.3) == "fluid"


def test_grade_free_flowing():
    assert _grade(0.1) == "free-flowing"


def test_batch_viscosity_returns_list():
    exprs = ["* * * * *", "0 9 * * 1", "bad"]
    results = batch_viscosity(exprs)
    assert len(results) == 3
    assert isinstance(results[0], ViscosityResult)


def test_str_with_error():
    result = assess_viscosity("nope")
    assert "error" in str(result).lower()


def test_str_without_error():
    result = assess_viscosity("0 6 * * *")
    s = str(result)
    assert "0 6 * * *" in s
    assert "score" in s
