"""Tests for crontab_buddy.complexity."""

import pytest
from crontab_buddy.complexity import score_expression, ComplexityResult


def test_all_wildcards_is_simple():
    result = score_expression("* * * * *")
    assert result is not None
    assert result.level == "simple"
    assert result.score == 0
    assert result.reasons == []


def test_plain_values_are_simple():
    result = score_expression("0 9 * * *")
    assert result is not None
    assert result.level == "simple"


def test_step_expression_adds_score():
    result = score_expression("*/5 * * * *")
    assert result is not None
    assert result.score >= 1
    assert any("step" in r for r in result.reasons)


def test_list_expression_adds_score():
    result = score_expression("0,15,30,45 * * * *")
    assert result is not None
    assert result.score >= 4
    assert any("list" in r for r in result.reasons)


def test_range_expression_adds_score():
    result = score_expression("0 9-17 * * *")
    assert result is not None
    assert any("range" in r for r in result.reasons)


def test_both_dom_and_dow_set_increases_score():
    result = score_expression("0 0 1 * 1")
    assert result is not None
    assert any("dom and dow" in r for r in result.reasons)
    assert result.score >= 2


def test_complex_expression_level():
    # multiple lists and steps
    result = score_expression("0,30 */2 1,15 1,6,12 1-5")
    assert result is not None
    assert result.level == "complex"


def test_moderate_expression_level():
    result = score_expression("*/15 * * * *")
    assert result is not None
    assert result.level in ("simple", "moderate")


def test_invalid_expression_returns_none():
    result = score_expression("not a cron")
    assert result is None


def test_too_few_fields_returns_none():
    result = score_expression("* * *")
    assert result is None


def test_result_str_contains_level():
    result = score_expression("0 9 * * *")
    assert result is not None
    assert "SIMPLE" in str(result) or "MODERATE" in str(result) or "COMPLEX" in str(result)


def test_result_str_contains_score():
    result = score_expression("*/5 * * * *")
    assert result is not None
    assert "score=" in str(result)


def test_result_is_dataclass():
    result = score_expression("0 0 * * *")
    assert isinstance(result, ComplexityResult)
    assert hasattr(result, "expression")
    assert hasattr(result, "score")
    assert hasattr(result, "level")
    assert hasattr(result, "reasons")
