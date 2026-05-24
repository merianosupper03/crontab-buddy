"""Tests for crontab_buddy.spacing."""
import pytest
from crontab_buddy.spacing import assess_spacing, batch_spacing, SpacingResult


def test_returns_spacing_result():
    result = assess_spacing("* * * * *")
    assert isinstance(result, SpacingResult)


def test_invalid_expression_has_error():
    result = assess_spacing("bad expr")
    assert result.error is not None
    assert result.score == 0.0


def test_every_minute_is_equidistant():
    result = assess_spacing("* * * * *")
    assert result.grade == "equidistant"


def test_every_minute_score_is_one():
    result = assess_spacing("* * * * *")
    assert result.score == pytest.approx(1.0, abs=0.01)


def test_every_minute_mean_interval_is_one():
    result = assess_spacing("* * * * *")
    assert result.mean_interval == pytest.approx(1.0, abs=0.01)


def test_every_minute_std_is_zero():
    result = assess_spacing("* * * * *")
    assert result.std_interval == pytest.approx(0.0, abs=0.01)


def test_every_15_minutes_is_equidistant():
    result = assess_spacing("*/15 * * * *")
    assert result.grade == "equidistant"
    assert result.score == pytest.approx(1.0, abs=0.01)


def test_every_15_minutes_mean_interval_is_15():
    result = assess_spacing("*/15 * * * *")
    assert result.mean_interval == pytest.approx(15.0, abs=0.1)


def test_single_firing_per_day_is_equidistant():
    # Only one firing minute — no intervals, treated as equidistant
    result = assess_spacing("0 12 * * *")
    assert result.score == pytest.approx(1.0, abs=0.01)
    assert result.intervals == []


def test_list_minutes_uneven_lowers_score():
    # 0,1,2,58,59 — clustered, should score below equidistant
    result = assess_spacing("0,1,2,58,59 * * * *")
    assert result.score < 0.9


def test_intervals_count_matches_firings_minus_one():
    result = assess_spacing("0,30 * * * *")
    # 48 firings per day → 47 intervals
    assert len(result.intervals) == len(
        [h * 60 + m for h in range(24) for m in [0, 30]]
    ) - 1


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 * * * *", "0 0 * * *", "*/5 * * * *", "1,7,13,29 * * * *"]:
        r = assess_spacing(expr)
        assert 0.0 <= r.score <= 1.0, f"score out of range for {expr!r}: {r.score}"


def test_str_representation_contains_grade():
    result = assess_spacing("* * * * *")
    assert result.grade in str(result)


def test_str_representation_error_contains_error():
    result = assess_spacing("not valid")
    assert "error" in str(result)


def test_batch_spacing_returns_list():
    results = batch_spacing(["* * * * *", "0 * * * *", "bad"])
    assert len(results) == 3
    assert all(isinstance(r, SpacingResult) for r in results)


def test_batch_spacing_error_entry():
    results = batch_spacing(["bad expression here"])
    assert results[0].error is not None
