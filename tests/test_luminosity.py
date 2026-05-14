"""Tests for crontab_buddy.luminosity."""

import pytest
from crontab_buddy.luminosity import (
    assess_luminosity,
    batch_luminosity,
    LuminosityResult,
    PEAK_HOURS,
)


def test_returns_luminosity_result():
    result = assess_luminosity("0 9 * * *")
    assert isinstance(result, LuminosityResult)


def test_invalid_expression_has_error():
    result = assess_luminosity("not valid")
    assert result.error is not None
    assert result.grade == "dark"
    assert result.score == 0.0


def test_single_peak_hour_is_radiant():
    # 9am is inside PEAK_HOURS
    result = assess_luminosity("0 9 * * *")
    assert result.error is None
    assert result.score == 1.0
    assert result.grade == "radiant"


def test_midnight_is_dark():
    # 0am is outside PEAK_HOURS
    result = assess_luminosity("0 0 * * *")
    assert result.error is None
    assert result.score == 0.0
    assert result.grade == "dark"


def test_all_hours_wildcard_moderate_score():
    # 10 of 24 hours are peak (8..17)
    result = assess_luminosity("*/15 * * * *")
    assert result.error is None
    expected = len(PEAK_HOURS) / 24
    assert abs(result.score - expected) < 0.01


def test_step_hours_partial_peak():
    # */6 -> hours 0, 6, 12, 18 -> 12 is peak, others not
    result = assess_luminosity("0 */6 * * *")
    assert result.error is None
    assert 0.0 < result.score < 1.0


def test_range_hours_all_peak():
    # 9-12 all inside PEAK_HOURS
    result = assess_luminosity("0 9-12 * * *")
    assert result.error is None
    assert result.score == 1.0


def test_list_hours_mixed():
    # hours 2 and 10: one peak, one not -> 0.5
    result = assess_luminosity("0 2,10 * * *")
    assert result.error is None
    assert abs(result.score - 0.5) < 0.01


def test_grade_bright():
    # hours 9,10,11,12,13 -> 5 peak out of 5 -> radiant
    result = assess_luminosity("0 9,10,11,12,13 * * *")
    assert result.grade == "radiant"


def test_grade_dim():
    # hours 1,2,3 -> all off-peak
    result = assess_luminosity("0 1,2,3 * * *")
    assert result.grade == "dark"


def test_peak_ratio_equals_score():
    result = assess_luminosity("30 14 * * 1")
    assert result.peak_ratio == result.score


def test_batch_luminosity_returns_list():
    exprs = ["0 9 * * *", "0 0 * * *", "*/15 * * * *"]
    results = batch_luminosity(exprs)
    assert len(results) == 3
    assert all(isinstance(r, LuminosityResult) for r in results)


def test_batch_luminosity_invalid_included():
    results = batch_luminosity(["bad expr", "0 9 * * *"])
    assert results[0].error is not None
    assert results[1].error is None


def test_str_with_error():
    result = assess_luminosity("bad")
    assert "error" in str(result).lower()


def test_str_without_error():
    result = assess_luminosity("0 10 * * *")
    assert "radiant" in str(result) or "bright" in str(result) or "grade" in str(result)
