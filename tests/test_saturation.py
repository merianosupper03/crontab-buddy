"""Tests for crontab_buddy.saturation."""
import pytest
from crontab_buddy.saturation import (
    assess_saturation,
    SaturationResult,
    _field_saturation,
    _grade,
    FIELD_RANGES,
)


def test_returns_saturation_result():
    result = assess_saturation("* * * * *")
    assert isinstance(result, SaturationResult)


def test_all_wildcards_is_saturated():
    result = assess_saturation("* * * * *")
    assert result.overall == pytest.approx(1.0)
    assert result.grade == "saturated"


def test_single_exact_time_is_minimal():
    result = assess_saturation("0 9 1 1 1")
    assert result.overall < 0.2
    assert result.grade == "minimal"


def test_invalid_expression_has_error():
    result = assess_saturation("bad expr")
    assert result.error is not None
    assert result.overall == 0.0


def test_scores_has_five_fields():
    result = assess_saturation("*/5 * * * *")
    assert set(result.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_step_minute_reduces_score():
    result = assess_saturation("*/5 * * * *")
    assert result.scores["minute"] == pytest.approx(1.0 / 5)


def test_range_field_partial_saturation():
    # 0-11 covers 12 out of 24 hours
    result = assess_saturation("0 0-11 * * *")
    assert result.scores["hour"] == pytest.approx(12 / 24)


def test_list_field_saturation():
    # 3 values out of 60 minutes
    result = assess_saturation("0,15,30 * * * *")
    assert result.scores["minute"] == pytest.approx(3 / 60)


def test_grade_saturated():
    assert _grade(0.9) == "saturated"


def test_grade_moderate():
    assert _grade(0.6) == "moderate"


def test_grade_sparse():
    assert _grade(0.3) == "sparse"


def test_grade_minimal():
    assert _grade(0.1) == "minimal"


def test_str_no_error():
    result = assess_saturation("* * * * *")
    s = str(result)
    assert "overall" in s
    assert "grade" in s


def test_str_with_error():
    result = assess_saturation("not valid")
    s = str(result)
    assert "error" in s


def test_field_saturation_wildcard():
    assert _field_saturation("*", 60) == 1.0


def test_field_saturation_exact():
    assert _field_saturation("5", 60) == pytest.approx(1 / 60)
