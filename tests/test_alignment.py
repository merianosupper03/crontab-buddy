"""Tests for crontab_buddy.alignment."""

import pytest
from crontab_buddy.alignment import assess_alignment, AlignmentResult, _grade


def test_returns_alignment_result():
    result = assess_alignment("0 0 * * *")
    assert isinstance(result, AlignmentResult)


def test_invalid_expression_returns_error():
    result = assess_alignment("bad expr")
    assert result.error is not None
    assert result.score == 0.0
    assert result.grade == "unaligned"


def test_midnight_anchor_matched():
    result = assess_alignment("0 0 * * *")
    assert "midnight anchor" in result.matched_patterns


def test_top_of_hour_matched():
    result = assess_alignment("0 * * * *")
    assert "top of hour" in result.matched_patterns


def test_specific_dow_matched():
    result = assess_alignment("0 9 * * 1")
    assert "specific dow" in result.matched_patterns


def test_specific_dom_matched():
    result = assess_alignment("0 9 1 * *")
    assert "specific dom" in result.matched_patterns


def test_wildcard_dom_and_dow_matched_for_hourly():
    result = assess_alignment("0 * * * *")
    assert "wildcard dom" in result.matched_patterns
    assert "wildcard dow" in result.matched_patterns


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 0 * * *", "30 6 1 * *", "*/5 * * * *"]:
        result = assess_alignment(expr)
        assert 0.0 <= result.score <= 1.0


def test_grade_well_aligned_for_high_score():
    assert _grade(0.75) == "well-aligned"
    assert _grade(1.0) == "well-aligned"


def test_grade_aligned_for_mid_score():
    assert _grade(0.5) == "aligned"
    assert _grade(0.6) == "aligned"


def test_grade_loosely_aligned():
    assert _grade(0.25) == "loosely-aligned"
    assert _grade(0.4) == "loosely-aligned"


def test_grade_unaligned_for_low_score():
    assert _grade(0.0) == "unaligned"
    assert _grade(0.1) == "unaligned"


def test_str_with_error():
    result = assess_alignment("not valid")
    assert "error" in str(result)


def test_str_without_error():
    result = assess_alignment("0 0 * * *")
    s = str(result)
    assert "score" in s
    assert "grade" in s


def test_matched_patterns_is_list():
    result = assess_alignment("0 0 * * *")
    assert isinstance(result.matched_patterns, list)


def test_every_minute_has_only_wildcard_patterns():
    result = assess_alignment("* * * * *")
    assert "midnight anchor" not in result.matched_patterns
    assert "top of hour" not in result.matched_patterns
