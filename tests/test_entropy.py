"""Tests for crontab_buddy.entropy."""

import pytest
from crontab_buddy.entropy import compute_entropy


def test_all_wildcards_is_predictable():
    result = compute_entropy("* * * * *")
    assert result.level == "predictable"
    assert result.score < 0.15


def test_specific_time_is_predictable():
    result = compute_entropy("30 9 * * *")
    assert result.level == "predictable"
    assert result.score < 0.4


def test_list_fields_raise_score():
    result = compute_entropy("0,15,30,45 * * * *")
    assert result.score > 0.0


def test_range_field_moderate():
    result = compute_entropy("0 9-17 * * 1-5")
    assert result.score >= 0.1


def test_step_expression_scores_above_zero():
    result = compute_entropy("*/5 * * * *")
    assert result.score > 0.0


def test_complex_expression_higher_than_simple():
    simple = compute_entropy("0 9 * * *")
    complex_ = compute_entropy("0,30 8-18 1,15 3,6,9,12 1-5")
    assert complex_.score > simple.score


def test_invalid_expression_returns_unknown():
    result = compute_entropy("not a cron")
    assert result.level == "unknown"
    assert result.score == 0.0
    assert any("parse error" in n for n in result.notes)


def test_dom_and_dow_both_set_adds_note():
    result = compute_entropy("0 12 15 * 1")
    assert any("DOM" in n for n in result.notes)


def test_dom_and_dow_both_set_bumps_score():
    without = compute_entropy("0 12 15 * *")
    with_dow = compute_entropy("0 12 15 * 1")
    assert with_dow.score >= without.score


def test_str_representation_contains_score():
    result = compute_entropy("0 9 * * *")
    assert str(result.score) in str(result) or "Entropy" in str(result)


def test_level_field_is_string():
    result = compute_entropy("*/10 */2 * * *")
    assert isinstance(result.level, str)
    assert result.level in {"predictable", "moderate", "irregular", "chaotic", "unknown"}


def test_score_bounded_between_zero_and_one():
    for expr in ["* * * * *", "*/1 * * * *", "0,5,10,15,20,25,30,35,40,45,50,55 * * * *"]:
        result = compute_entropy(expr)
        assert 0.0 <= result.score <= 1.0
