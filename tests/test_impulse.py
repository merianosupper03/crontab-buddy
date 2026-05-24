"""Tests for crontab_buddy.impulse."""

import pytest
from crontab_buddy.impulse import (
    assess_impulse, batch_impulse, ImpulseResult, _grade, _firing_minutes
)
from crontab_buddy.parser import CronExpression


def test_returns_impulse_result():
    result = assess_impulse("* * * * *")
    assert isinstance(result, ImpulseResult)


def test_invalid_expression_has_error():
    result = assess_impulse("bad expr")
    assert result.error is not None
    assert result.score == 0.0


def test_every_minute_score_near_zero():
    # Perfectly uniform spacing → low impulse
    result = assess_impulse("* * * * *")
    assert result.score < 0.1


def test_single_exact_time_is_explosive():
    result = assess_impulse("30 6 * * *")
    assert result.grade == "explosive"
    assert result.score == 1.0


def test_every_minute_grade_is_flat():
    result = assess_impulse("* * * * *")
    assert result.grade == "flat"


def test_firing_count_every_minute():
    result = assess_impulse("* * * * *")
    assert result.firing_count == 1440


def test_firing_count_hourly():
    result = assess_impulse("0 * * * *")
    assert result.firing_count == 24


def test_firing_count_single():
    result = assess_impulse("0 12 * * *")
    assert result.firing_count == 1


def test_score_between_zero_and_one():
    for expr in ["*/5 * * * *", "0,30 * * * *", "0 9-17 * * 1-5"]:
        r = assess_impulse(expr)
        assert 0.0 <= r.score <= 1.0


def test_grade_explosive():
    assert _grade(0.9) == "explosive"


def test_grade_sharp():
    assert _grade(0.7) == "sharp"


def test_grade_moderate():
    assert _grade(0.5) == "moderate"


def test_grade_gentle():
    assert _grade(0.3) == "gentle"


def test_grade_flat():
    assert _grade(0.1) == "flat"


def test_batch_impulse_returns_list():
    results = batch_impulse(["* * * * *", "0 12 * * *"])
    assert len(results) == 2
    assert all(isinstance(r, ImpulseResult) for r in results)


def test_batch_impulse_handles_invalid():
    results = batch_impulse(["bad", "* * * * *"])
    assert results[0].error is not None
    assert results[1].error is None


def test_str_with_error():
    result = assess_impulse("not valid")
    assert "error=" in str(result)


def test_str_without_error():
    result = assess_impulse("* * * * *")
    s = str(result)
    assert "score=" in s
    assert "grade=" in s
