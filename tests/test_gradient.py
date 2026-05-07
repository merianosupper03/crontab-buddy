"""Tests for crontab_buddy.gradient"""

import pytest
from crontab_buddy.gradient import compute_gradient, GradientResult


def test_returns_gradient_result():
    result = compute_gradient("* * * * *")
    assert isinstance(result, GradientResult)


def test_every_minute_is_smooth():
    result = compute_gradient("* * * * *")
    # Every minute fires 60 times with gap=1 — perfectly uniform
    assert result.label == "smooth"
    assert result.score >= 0.85


def test_every_minute_has_no_error():
    result = compute_gradient("* * * * *")
    assert result.error is None


def test_single_firing_is_spiky():
    result = compute_gradient("30 * * * *")
    # Only one minute per hour — no gaps to measure
    assert result.label == "spiky"
    assert result.score == 0.0


def test_step_every_15_minutes_is_smooth():
    result = compute_gradient("*/15 * * * *")
    # Fires at 0, 15, 30, 45 — equal gaps
    assert result.label in ("smooth", "gradual")
    assert result.score > 0.5


def test_step_every_2_minutes_is_smooth():
    result = compute_gradient("*/2 * * * *")
    assert result.score >= 0.85


def test_list_expression_uneven():
    # Fires at 0 and 59 — very uneven
    result = compute_gradient("0,59 * * * *")
    assert result.score < 0.85


def test_invalid_expression_returns_error():
    result = compute_gradient("invalid")
    assert result.error is not None
    assert result.score == 0.0
    assert result.label == "spiky"


def test_deltas_are_empty_for_single_firing():
    result = compute_gradient("0 * * * *")
    assert result.deltas == []


def test_deltas_are_present_for_multiple_firings():
    result = compute_gradient("*/10 * * * *")
    # Fires at 0, 10, 20, 30, 40, 50 — 5 gaps of 10
    assert len(result.deltas) == 5
    assert all(d == 10 for d in result.deltas)


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 * * * *", "*/5 * * * *", "1,7,23,55 * * * *"]:
        result = compute_gradient(expr)
        assert 0.0 <= result.score <= 1.0, f"Score out of range for {expr}: {result.score}"


def test_str_representation_with_error():
    result = compute_gradient("bad expr")
    s = str(result)
    assert "error" in s


def test_str_representation_without_error():
    result = compute_gradient("*/5 * * * *")
    s = str(result)
    assert "Gradient" in s
    assert result.label in s
