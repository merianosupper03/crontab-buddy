"""Tests for crontab_buddy.regularity."""

import pytest

from crontab_buddy.regularity import (
    RegularityResult,
    _field_regularity,
    assess_regularity,
    batch_regularity,
)


# --- _field_regularity ---

def test_field_wildcard_is_one():
    assert _field_regularity("*") == 1.0


def test_field_plain_integer_is_one():
    assert _field_regularity("5") == 1.0


def test_field_list_lower_than_one():
    score = _field_regularity("1,2,3")
    assert score < 1.0
    assert score >= 0.3


def test_field_range_moderate():
    score = _field_regularity("1-5")
    assert 0.4 <= score <= 0.9


def test_field_step_star_moderate():
    score = _field_regularity("*/5")
    assert 0.3 <= score <= 1.0


def test_field_step_one_is_high():
    score = _field_regularity("*/1")
    assert score >= 0.9


# --- assess_regularity ---

def test_returns_regularity_result():
    result = assess_regularity("0 * * * *")
    assert isinstance(result, RegularityResult)


def test_every_minute_is_highly_regular():
    result = assess_regularity("* * * * *")
    assert result.level == "highly regular"
    assert result.score >= 0.85


def test_specific_time_is_highly_regular():
    result = assess_regularity("30 6 * * *")
    assert result.score >= 0.85


def test_complex_list_expression_lower_score():
    result = assess_regularity("1,15,30,45 0,6,12,18 * * *")
    assert result.score < 0.85


def test_invalid_expression_has_error():
    result = assess_regularity("99 99 99")
    assert result.error is not None
    assert result.score == 0.0
    assert result.level == "irregular"


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 0 * * *", "*/5 * * * *", "1,2 3,4 * * *"]:
        r = assess_regularity(expr)
        assert 0.0 <= r.score <= 1.0


def test_description_contains_level():
    result = assess_regularity("0 0 * * *")
    assert result.level in result.description


def test_str_no_error():
    result = assess_regularity("0 0 * * *")
    text = str(result)
    assert "score=" in text
    assert "level=" in text


def test_str_with_error():
    result = assess_regularity("bad")
    text = str(result)
    assert "error=" in text


# --- batch_regularity ---

def test_batch_returns_list():
    results = batch_regularity(["* * * * *", "0 0 * * *"])
    assert len(results) == 2
    assert all(isinstance(r, RegularityResult) for r in results)


def test_batch_empty_list():
    assert batch_regularity([]) == []


def test_batch_preserves_order():
    exprs = ["* * * * *", "0 0 * * *", "*/5 * * * *"]
    results = batch_regularity(exprs)
    for r, e in zip(results, exprs):
        assert r.expression == e
