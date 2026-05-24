"""Tests for crontab_buddy.symmetry_score."""
import json
import pytest
from crontab_buddy.symmetry_score import compute_symmetry_score, SymmetryScoreResult


def test_returns_symmetry_score_result():
    result = compute_symmetry_score("* * * * *")
    assert isinstance(result, SymmetryScoreResult)


def test_invalid_expression_has_error():
    result = compute_symmetry_score("bad expr")
    assert result.error is not None
    assert result.score == 0.0


def test_every_minute_is_balanced():
    result = compute_symmetry_score("* * * * *")
    assert result.grade == "balanced"
    assert result.score >= 0.9


def test_every_minute_firing_count_is_60():
    result = compute_symmetry_score("* * * * *")
    assert result.firing_count == 60


def test_every_five_minutes_is_balanced():
    result = compute_symmetry_score("*/5 * * * *")
    assert result.grade == "balanced"
    assert result.score >= 0.9


def test_every_fifteen_minutes_is_balanced():
    result = compute_symmetry_score("*/15 * * * *")
    assert result.grade == "balanced"
    assert result.score >= 0.9


def test_single_firing_is_asymmetric():
    result = compute_symmetry_score("30 * * * *")
    assert result.grade == "asymmetric"
    assert result.score == 0.0
    assert result.firing_count == 1


def test_two_equidistant_firings_is_balanced():
    result = compute_symmetry_score("0,30 * * * *")
    assert result.score >= 0.9


def test_list_uneven_lowers_score():
    result = compute_symmetry_score("0,1,2,50 * * * *")
    assert result.score < 0.9


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 * * * *", "*/10 * * * *", "1,2,45 * * * *"]:
        result = compute_symmetry_score(expr)
        assert 0.0 <= result.score <= 1.0


def test_grade_is_string():
    result = compute_symmetry_score("*/5 * * * *")
    assert isinstance(result.grade, str)
    assert len(result.grade) > 0


def test_str_representation_no_error():
    result = compute_symmetry_score("*/5 * * * *")
    s = str(result)
    assert "SymmetryScore" in s
    assert "score=" in s


def test_str_representation_with_error():
    result = compute_symmetry_score("not valid")
    s = str(result)
    assert "error=" in s


def test_range_field_fires_correctly():
    result = compute_symmetry_score("10-14 * * * *")
    assert result.firing_count == 5
