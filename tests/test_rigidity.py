"""Tests for crontab_buddy.rigidity."""

import pytest
from crontab_buddy.rigidity import (
    assess_rigidity,
    batch_rigidity,
    _field_rigidity,
    _grade,
    RigidityResult,
)


def test_returns_rigidity_result():
    result = assess_rigidity("0 9 * * 1")
    assert isinstance(result, RigidityResult)


def test_invalid_expression_has_error():
    result = assess_rigidity("not valid")
    assert result.error != ""
    assert result.grade == "unknown"


def test_all_wildcards_is_supple():
    result = assess_rigidity("* * * * *")
    assert result.score == 0.0
    assert result.grade == "supple"


def test_all_exact_values_is_ironclad_or_rigid():
    result = assess_rigidity("30 9 15 6 2")
    assert result.score > 0.8
    assert result.grade in ("ironclad", "rigid")


def test_scores_dict_has_five_keys():
    result = assess_rigidity("* * * * *")
    assert set(result.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_wildcard_field_rigidity_is_zero():
    assert _field_rigidity("*", 59) == 0.0


def test_plain_integer_field_rigidity_is_one():
    assert _field_rigidity("30", 59) == 1.0


def test_step_field_rigidity_between_zero_and_one():
    val = _field_rigidity("*/15", 59)
    assert 0.0 < val <= 1.0


def test_range_field_rigidity_between_zero_and_one():
    val = _field_rigidity("9-17", 23)
    assert 0.0 <= val <= 1.0


def test_list_field_rigidity_decreases_with_more_values():
    few = _field_rigidity("1,2", 59)
    many = _field_rigidity("1,2,3,4,5,6,7,8", 59)
    assert few > many


def test_grade_supple():
    assert _grade(0.1) == "supple"


def test_grade_pliable():
    assert _grade(0.3) == "pliable"


def test_grade_firm():
    assert _grade(0.5) == "firm"


def test_grade_rigid():
    assert _grade(0.7) == "rigid"


def test_grade_ironclad():
    assert _grade(0.9) == "ironclad"


def test_batch_rigidity_returns_list():
    results = batch_rigidity(["* * * * *", "0 9 * * 1"])
    assert len(results) == 2
    assert all(isinstance(r, RigidityResult) for r in results)


def test_batch_rigidity_handles_invalid():
    results = batch_rigidity(["bad expr", "0 9 * * 1"])
    assert results[0].error != ""
    assert results[1].error == ""


def test_score_between_zero_and_one():
    for expr in ["*/5 * * * *", "0 12 * * *", "0 0 1 1 *"]:
        r = assess_rigidity(expr)
        assert 0.0 <= r.score <= 1.0
