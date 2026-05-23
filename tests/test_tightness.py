"""Tests for crontab_buddy.tightness."""
import pytest
from crontab_buddy.tightness import (
    assess_tightness, batch_tightness, _field_tightness, _grade,
    TightnessResult,
)


def test_returns_tightness_result():
    r = assess_tightness("* * * * *")
    assert isinstance(r, TightnessResult)


def test_invalid_expression_has_error():
    r = assess_tightness("bad expression")
    assert r.error is not None
    assert r.score == 0.0
    assert r.grade == "unbounded"


def test_all_wildcards_is_unbounded():
    r = assess_tightness("* * * * *")
    assert r.grade == "unbounded"
    assert r.score == pytest.approx(0.0)


def test_all_exact_values_is_tight_or_ironclad():
    r = assess_tightness("30 9 15 6 1")
    assert r.grade in ("tight", "ironclad")
    assert r.score > 0.7


def test_scores_dict_has_five_keys():
    r = assess_tightness("0 12 * * *")
    assert set(r.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_exact_minute_scores_one():
    assert _field_tightness("30") == pytest.approx(1.0)


def test_wildcard_scores_zero():
    assert _field_tightness("*") == pytest.approx(0.0)


def test_step_wildcard_scores_between_zero_and_one():
    s = _field_tightness("*/15")
    assert 0.0 < s < 1.0


def test_range_scores_between_zero_and_one():
    s = _field_tightness("9-17")
    assert 0.0 < s <= 1.0


def test_list_scores_above_zero():
    s = _field_tightness("1,2,3")
    assert s > 0.0


def test_grade_ironclad():
    assert _grade(0.90) == "ironclad"


def test_grade_tight():
    assert _grade(0.75) == "tight"


def test_grade_moderate():
    assert _grade(0.55) == "moderate"


def test_grade_loose():
    assert _grade(0.35) == "loose"


def test_grade_slack():
    assert _grade(0.15) == "slack"


def test_grade_unbounded():
    assert _grade(0.05) == "unbounded"


def test_batch_tightness_returns_list():
    results = batch_tightness(["* * * * *", "0 9 * * 1"])
    assert len(results) == 2
    assert all(isinstance(r, TightnessResult) for r in results)


def test_batch_tightness_handles_invalid():
    results = batch_tightness(["* * * * *", "not valid"])
    assert results[1].error is not None


def test_specific_daily_time_is_moderate_or_above():
    r = assess_tightness("0 9 * * *")
    assert r.score >= 0.3


def test_str_with_error():
    r = assess_tightness("bad")
    assert "error" in str(r).lower()


def test_str_without_error():
    r = assess_tightness("0 0 * * *")
    assert "TightnessResult" in str(r)
    assert "score" in str(r)
