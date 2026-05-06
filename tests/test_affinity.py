"""Tests for crontab_buddy.affinity."""

import pytest
from crontab_buddy.affinity import assess_affinity, AffinityResult


def test_returns_affinity_result():
    result = assess_affinity("0 * * * *", "30 * * * *")
    assert isinstance(result, AffinityResult)


def test_identical_expressions_poor_grade():
    result = assess_affinity("0 * * * *", "0 * * * *")
    assert result.grade in ("Poor", "Fair")
    assert result.overlap_count > 0


def test_non_overlapping_expressions_have_zero_overlap():
    # one fires at minute 0, other at minute 30 — no shared minute
    result = assess_affinity("0 1 * * *", "30 2 * * *")
    assert result.overlap_count == 0


def test_score_between_zero_and_one():
    result = assess_affinity("*/5 * * * *", "*/7 * * * *")
    assert 0.0 <= result.score <= 1.0


def test_invalid_expr_a_returns_poor():
    result = assess_affinity("not a cron", "0 * * * *")
    assert result.grade == "Poor"
    assert result.score == 0.0
    assert any("Invalid expression A" in n for n in result.notes)


def test_invalid_expr_b_returns_poor():
    result = assess_affinity("0 * * * *", "bad expression")
    assert result.grade == "Poor"
    assert result.score == 0.0
    assert any("Invalid expression B" in n for n in result.notes)


def test_str_contains_score():
    result = assess_affinity("0 * * * *", "30 * * * *")
    text = str(result)
    assert "Score" in text
    assert "Grade" in text


def test_str_contains_expressions():
    result = assess_affinity("0 6 * * *", "0 18 * * *")
    text = str(result)
    assert "0 6 * * *" in text
    assert "0 18 * * *" in text


def test_grade_labels_are_valid():
    valid_grades = {"Excellent", "Good", "Fair", "Poor"}
    result = assess_affinity("0 * * * *", "15 * * * *")
    assert result.grade in valid_grades


def test_overlap_count_is_non_negative():
    result = assess_affinity("*/10 * * * *", "*/15 * * * *")
    assert result.overlap_count >= 0
