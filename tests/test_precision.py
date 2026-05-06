"""Tests for crontab_buddy.precision."""

import pytest
from crontab_buddy.precision import assess_precision, _field_precision, PrecisionResult


# --- _field_precision unit tests ---

def test_wildcard_is_zero():
    assert _field_precision("*") == 0.0


def test_plain_integer_is_one():
    assert _field_precision("30") == 1.0


def test_step_expression_between_zero_and_one():
    score = _field_precision("*/15")
    assert 0.0 < score < 1.0


def test_larger_step_gives_higher_precision():
    assert _field_precision("*/30") > _field_precision("*/5")


def test_range_expression_is_partial():
    score = _field_precision("1-5")
    assert 0.0 < score < 1.0


def test_list_expression_lowers_precision():
    score = _field_precision("1,2,3,4,5")
    assert score < 1.0


# --- assess_precision integration tests ---

def test_returns_precision_result():
    result = assess_precision("30 6 * * *")
    assert isinstance(result, PrecisionResult)


def test_exact_time_has_high_score():
    result = assess_precision("30 6 15 3 *")
    assert result.score >= 0.6


def test_every_minute_has_low_score():
    result = assess_precision("* * * * *")
    assert result.score == 0.0


def test_every_minute_is_diffuse():
    result = assess_precision("* * * * *")
    assert result.level == "diffuse"


def test_specific_time_is_precise_or_exact():
    result = assess_precision("0 12 * * 1")
    assert result.level in ("precise", "exact", "moderate")


def test_invalid_expression_returns_error():
    result = assess_precision("not a cron")
    assert result.error != ""
    assert result.score == 0.0
    assert result.level == "unknown"


def test_invalid_expression_str_contains_error():
    result = assess_precision("bad")
    assert "error" in str(result).lower()


def test_valid_result_str_contains_score():
    result = assess_precision("0 0 * * *")
    assert "score" in str(result)
    assert result.expression == "0 0 * * *"


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 6 * * *", "*/15 * * * *", "0 0 1 1 *"]:
        result = assess_precision(expr)
        assert 0.0 <= result.score <= 1.0, f"Out of range for {expr}"


def test_description_mentions_precision():
    result = assess_precision("0 9 * * 1-5")
    assert "precision" in result.description.lower()
