"""Tests for crontab_buddy.acuity."""

import pytest
from crontab_buddy.acuity import assess_acuity, batch_acuity, AcuityResult


def test_returns_acuity_result():
    result = assess_acuity("0 9 * * 1")
    assert isinstance(result, AcuityResult)


def test_invalid_expression_has_error():
    result = assess_acuity("not valid")
    assert result.error is not None
    assert result.score == 0.0
    assert result.grade == "diffuse"


def test_all_wildcards_is_diffuse():
    result = assess_acuity("* * * * *")
    assert result.grade == "diffuse"
    assert result.score == 0.0


def test_all_exact_values_is_pinpoint():
    result = assess_acuity("30 9 15 6 2")
    assert result.grade == "pinpoint"
    assert result.score == pytest.approx(1.0)


def test_scores_dict_has_five_keys():
    result = assess_acuity("0 12 * * *")
    assert set(result.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_exact_minute_scores_one():
    result = assess_acuity("5 * * * *")
    assert result.scores["minute"] == pytest.approx(1.0)


def test_wildcard_minute_scores_zero():
    result = assess_acuity("* * * * *")
    assert result.scores["minute"] == pytest.approx(0.0)


def test_step_expression_scores_above_zero():
    result = assess_acuity("*/15 * * * *")
    assert result.scores["minute"] > 0.0


def test_list_expression_scores_above_zero():
    result = assess_acuity("0,30 * * * *")
    assert result.scores["minute"] > 0.0


def test_range_expression_partial_score():
    result = assess_acuity("0 9-17 * * *")
    assert 0.0 < result.scores["hour"] < 1.0


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 9 * * 1", "30 9 15 6 2", "*/5 */2 * * *"]:
        r = assess_acuity(expr)
        assert 0.0 <= r.score <= 1.0


def test_grade_values_are_valid():
    valid_grades = {"pinpoint", "focused", "moderate", "broad", "diffuse"}
    for expr in ["* * * * *", "0 9 * * 1", "30 9 15 6 2"]:
        r = assess_acuity(expr)
        assert r.grade in valid_grades


def test_str_representation_no_error():
    result = assess_acuity("0 9 * * *")
    s = str(result)
    assert "score" in s
    assert "grade" in s


def test_str_representation_with_error():
    result = assess_acuity("bad expr")
    s = str(result)
    assert "error" in s


def test_batch_acuity_returns_list():
    results = batch_acuity(["* * * * *", "0 9 * * 1"])
    assert len(results) == 2
    assert all(isinstance(r, AcuityResult) for r in results)


def test_batch_acuity_preserves_order():
    exprs = ["* * * * *", "0 9 * * 1", "30 9 15 6 2"]
    results = batch_acuity(exprs)
    for expr, result in zip(exprs, results):
        assert result.expression == expr
