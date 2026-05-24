"""Tests for crontab_buddy.equilibrium."""

import pytest
from crontab_buddy.equilibrium import (
    assess_equilibrium,
    batch_equilibrium,
    EquilibriumResult,
    _grade,
    _field_equilibrium,
)


def test_returns_equilibrium_result():
    result = assess_equilibrium("* * * * *")
    assert isinstance(result, EquilibriumResult)


def test_invalid_expression_has_error():
    result = assess_equilibrium("bad expr")
    assert result.error is not None
    assert result.score == 0.0
    assert result.grade == "chaotic"


def test_all_wildcards_is_harmonious():
    result = assess_equilibrium("* * * * *")
    assert result.score == 1.0
    assert result.grade == "harmonious"


def test_single_exact_time_has_low_score():
    result = assess_equilibrium("30 6 15 6 3")
    assert result.score < 0.5


def test_scores_dict_has_five_keys():
    result = assess_equilibrium("* * * * *")
    assert set(result.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_step_expression_improves_score():
    exact = assess_equilibrium("5 5 5 5 5")
    step = assess_equilibrium("*/5 */5 */5 */5 */5")
    assert step.score > exact.score


def test_grade_harmonious():
    assert _grade(0.9) == "harmonious"


def test_grade_balanced():
    assert _grade(0.7) == "balanced"


def test_grade_uneven():
    assert _grade(0.5) == "uneven"


def test_grade_lopsided():
    assert _grade(0.3) == "lopsided"


def test_grade_chaotic():
    assert _grade(0.1) == "chaotic"


def test_field_equilibrium_wildcard():
    assert _field_equilibrium("*", 60) == 1.0


def test_field_equilibrium_step():
    val = _field_equilibrium("*/10", 60)
    assert 0.0 < val < 1.0


def test_field_equilibrium_list():
    val = _field_equilibrium("1,2,3", 60)
    assert val == round(3 / 60, 4)


def test_field_equilibrium_range():
    val = _field_equilibrium("0-11", 24)
    assert val == round(12 / 24, 4)


def test_field_equilibrium_exact():
    val = _field_equilibrium("5", 60)
    assert val == 0.1


def test_batch_equilibrium_returns_list():
    results = batch_equilibrium(["* * * * *", "0 0 * * *", "bad"])
    assert len(results) == 3
    assert all(isinstance(r, EquilibriumResult) for r in results)


def test_str_with_error():
    result = assess_equilibrium("not valid")
    assert "error=" in str(result)


def test_str_without_error():
    result = assess_equilibrium("* * * * *")
    s = str(result)
    assert "harmonious" in s
    assert "1.0" in s
