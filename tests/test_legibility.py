"""Tests for crontab_buddy.legibility."""

import pytest
from crontab_buddy.legibility import assess_legibility, _field_legibility, _grade


def test_returns_legibility_result():
    result = assess_legibility("0 9 * * 1")
    assert result.expression == "0 9 * * 1"
    assert isinstance(result.score, float)
    assert isinstance(result.grade, str)
    assert isinstance(result.field_scores, dict)


def test_all_wildcards_is_transparent():
    result = assess_legibility("* * * * *")
    assert result.score >= 0.85
    assert result.grade == "transparent"


def test_invalid_expression_has_error():
    result = assess_legibility("not a cron")
    assert result.error is not None
    assert result.score == 0.0
    assert result.grade == "opaque"


def test_plain_integers_score_high():
    result = assess_legibility("30 8 1 1 0")
    assert result.score >= 0.85


def test_step_on_wildcard_is_readable():
    result = assess_legibility("*/5 * * * *")
    # */5 field gets 0.65, rest are wildcards at 1.0
    assert result.score >= 0.80


def test_list_field_lowers_score():
    result_simple = assess_legibility("0 9 * * *")
    result_list = assess_legibility("0,15,30,45 9 * * *")
    assert result_list.score < result_simple.score


def test_field_scores_has_five_keys():
    result = assess_legibility("0 12 * * *")
    assert set(result.field_scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_grade_transparent():
    assert _grade(0.90) == "transparent"
    assert _grade(0.85) == "transparent"


def test_grade_clear():
    assert _grade(0.70) == "clear"
    assert _grade(0.65) == "clear"


def test_grade_readable():
    assert _grade(0.50) == "readable"


def test_grade_murky():
    assert _grade(0.30) == "murky"


def test_grade_opaque():
    assert _grade(0.10) == "opaque"
    assert _grade(0.0) == "opaque"


def test_field_legibility_wildcard():
    assert _field_legibility("*") == 1.0


def test_field_legibility_plain_int():
    assert _field_legibility("5") == 0.95


def test_field_legibility_range():
    score = _field_legibility("9-17")
    assert 0.60 <= score <= 0.80


def test_field_legibility_step_wildcard():
    score = _field_legibility("*/10")
    assert score == 0.65


def test_field_legibility_step_range():
    score = _field_legibility("1-5/2")
    assert score < 0.65


def test_str_with_error():
    result = assess_legibility("bad expr")
    s = str(result)
    assert "error=" in s


def test_str_without_error():
    result = assess_legibility("0 0 * * *")
    s = str(result)
    assert "score=" in s
    assert "grade=" in s
