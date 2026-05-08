"""Tests for crontab_buddy.turbulence."""

import pytest

from crontab_buddy.turbulence import (
    TurbulenceResult,
    assess_turbulence,
    batch_turbulence,
    _firing_minutes_per_hour,
)
from crontab_buddy.parser import CronExpression


# ---------------------------------------------------------------------------
# _firing_minutes_per_hour
# ---------------------------------------------------------------------------

def test_wildcard_minute_gives_all_60():
    expr = CronExpression("* * * * *")
    minutes = _firing_minutes_per_hour(expr)
    assert minutes == list(range(60))


def test_plain_minute_gives_single_value():
    expr = CronExpression("30 * * * *")
    minutes = _firing_minutes_per_hour(expr)
    assert minutes == [30]


def test_step_minute_gives_correct_values():
    expr = CronExpression("*/15 * * * *")
    minutes = _firing_minutes_per_hour(expr)
    assert minutes == [0, 15, 30, 45]


def test_range_minute_gives_correct_values():
    expr = CronExpression("0-4 * * * *")
    minutes = _firing_minutes_per_hour(expr)
    assert minutes == [0, 1, 2, 3, 4]


def test_list_minute_gives_correct_values():
    expr = CronExpression("0,20,40 * * * *")
    minutes = _firing_minutes_per_hour(expr)
    assert minutes == [0, 20, 40]


# ---------------------------------------------------------------------------
# assess_turbulence
# ---------------------------------------------------------------------------

def test_returns_turbulence_result():
    result = assess_turbulence("* * * * *")
    assert isinstance(result, TurbulenceResult)


def test_every_minute_is_smooth():
    result = assess_turbulence("* * * * *")
    assert result.label == "smooth"
    assert result.score < 0.15


def test_every_minute_has_no_error():
    result = assess_turbulence("* * * * *")
    assert result.error is None


def test_single_firing_is_turbulent():
    result = assess_turbulence("30 12 * * *")
    assert result.label == "turbulent"
    assert result.score == 1.0


def test_uniform_step_is_smooth_or_gentle():
    result = assess_turbulence("*/10 * * * *")
    assert result.score < 0.35
    assert result.label in ("smooth", "gentle")


def test_intervals_populated_for_multi_firing():
    result = assess_turbulence("0,15,30,45 * * * *")
    assert result.intervals == [15, 15, 15]


def test_invalid_expression_returns_error():
    result = assess_turbulence("99 * * *")
    assert result.error is not None
    assert result.label == "unknown"


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 * * * *", "*/5 * * * *", "0,30 * * * *"]:
        result = assess_turbulence(expr)
        assert 0.0 <= result.score <= 1.0


# ---------------------------------------------------------------------------
# batch_turbulence
# ---------------------------------------------------------------------------

def test_batch_returns_list():
    results = batch_turbulence(["* * * * *", "0 12 * * *"])
    assert len(results) == 2


def test_batch_preserves_order():
    exprs = ["* * * * *", "0 12 * * *", "*/5 * * * *"]
    results = batch_turbulence(exprs)
    assert [r.expression for r in results] == exprs
