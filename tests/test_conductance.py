"""Tests for crontab_buddy.conductance."""

import pytest
from crontab_buddy.conductance import (
    assess_conductance,
    batch_conductance,
    ConductanceResult,
    TOTAL_MINUTES_PER_DAY,
)


def test_returns_conductance_result():
    result = assess_conductance("* * * * *")
    assert isinstance(result, ConductanceResult)


def test_every_minute_is_superconducting():
    result = assess_conductance("* * * * *")
    assert result.grade == "superconducting"


def test_every_minute_score_is_one():
    result = assess_conductance("* * * * *")
    assert result.score == pytest.approx(1.0)


def test_every_minute_active_minutes_is_1440():
    result = assess_conductance("* * * * *")
    assert result.active_minutes == TOTAL_MINUTES_PER_DAY


def test_single_exact_time_is_insulating_or_low():
    result = assess_conductance("30 9 * * *")
    assert result.grade in ("insulating", "low conductance")


def test_single_exact_time_active_minutes_is_one():
    result = assess_conductance("30 9 * * *")
    assert result.active_minutes == 1


def test_hourly_expression_is_low_or_resistive():
    result = assess_conductance("0 * * * *")
    assert result.grade in ("insulating", "low conductance", "resistive")
    assert result.active_minutes == 24


def test_every_five_minutes_score():
    result = assess_conductance("*/5 * * * *")
    # 12 minutes * 24 hours = 288 active
    assert result.active_minutes == 288
    assert result.score == pytest.approx(288 / 1440, rel=1e-3)


def test_invalid_expression_has_error():
    result = assess_conductance("bad expression")
    assert result.error is not None
    assert result.score == 0.0
    assert result.grade == "insulating"


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 12 * * *", "*/15 * * * *", "0 0 * * 0"]:
        r = assess_conductance(expr)
        assert 0.0 <= r.score <= 1.0


def test_batch_conductance_returns_list():
    results = batch_conductance(["* * * * *", "0 12 * * *"])
    assert len(results) == 2
    assert all(isinstance(r, ConductanceResult) for r in results)


def test_batch_conductance_handles_invalid():
    results = batch_conductance(["* * * * *", "not valid"])
    assert results[0].error is None
    assert results[1].error is not None


def test_str_with_error():
    result = assess_conductance("bad")
    assert "error" in str(result).lower()


def test_str_without_error():
    result = assess_conductance("* * * * *")
    s = str(result)
    assert "superconducting" in s
    assert "1440" in s
