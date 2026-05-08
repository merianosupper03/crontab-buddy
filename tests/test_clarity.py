"""Tests for crontab_buddy.clarity."""

import pytest
from crontab_buddy.clarity import assess_clarity, ClarityResult, _field_clarity


def test_returns_clarity_result():
    result = assess_clarity("0 9 * * 1")
    assert isinstance(result, ClarityResult)


def test_all_wildcards_is_crystal():
    result = assess_clarity("* * * * *")
    assert result.grade == "crystal"
    assert result.score == pytest.approx(1.0)


def test_invalid_expression_has_error():
    result = assess_clarity("not valid")
    assert result.error is not None
    assert result.grade == "opaque"
    assert result.score == 0.0


def test_plain_integers_score_high():
    result = assess_clarity("30 8 1 1 *")
    assert result.score >= 0.8


def test_step_on_wildcard_is_reasonably_clear():
    result = assess_clarity("*/15 * * * *")
    assert result.score >= 0.7


def test_complex_list_lowers_score():
    # many comma-separated values should reduce clarity
    result = assess_clarity("1,2,3,4,5,6,7 * * * *")
    assert result.score < assess_clarity("* * * * *").score


def test_dom_and_dow_both_set_adds_hint():
    result = assess_clarity("0 12 15 * 1")
    assert any("DOM" in h or "DOW" in h for h in result.hints)


def test_no_hints_for_simple_expression():
    result = assess_clarity("0 0 * * *")
    assert result.hints == []


def test_grade_crystal_threshold():
    result = assess_clarity("* * * * *")
    assert result.grade == "crystal"


def test_grade_opaque_for_invalid():
    result = assess_clarity("60 25 * * *")
    assert result.grade == "opaque"


def test_field_clarity_wildcard():
    assert _field_clarity("*") == pytest.approx(1.0)


def test_field_clarity_plain_integer():
    assert _field_clarity("5") == pytest.approx(1.0)


def test_field_clarity_step_wildcard():
    assert _field_clarity("*/10") == pytest.approx(0.75)


def test_field_clarity_range():
    score = _field_clarity("9-17")
    assert 0.5 <= score <= 0.8


def test_field_clarity_list_three_items():
    score = _field_clarity("1,15,30")
    assert 0.4 <= score <= 0.7


def test_str_representation_no_error():
    result = assess_clarity("0 6 * * *")
    s = str(result)
    assert "0 6 * * *" in s
    assert "score=" in s


def test_str_representation_with_error():
    result = assess_clarity("bad expr")
    s = str(result)
    assert "ERROR" in s
