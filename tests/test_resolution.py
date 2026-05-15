"""Tests for crontab_buddy.resolution."""

import pytest
from crontab_buddy.resolution import (
    assess_resolution,
    batch_resolution,
    ResolutionResult,
    _field_resolution,
    _grade,
)


def test_returns_resolution_result():
    r = assess_resolution("* * * * *")
    assert isinstance(r, ResolutionResult)


def test_invalid_expression_has_error():
    r = assess_resolution("bad expression")
    assert r.error is not None
    assert r.score == 0.0
    assert r.grade == "blunt"


def test_all_wildcards_is_atomic_or_fine():
    r = assess_resolution("* * * * *")
    assert r.grade in ("atomic", "fine")
    assert r.score >= 0.65


def test_single_exact_time_is_coarse_or_blunt():
    r = assess_resolution("0 9 1 1 1")
    assert r.grade in ("coarse", "blunt")
    assert r.score < 0.45


def test_scores_dict_has_five_keys():
    r = assess_resolution("*/5 * * * *")
    assert set(r.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_step_minute_lowers_score_vs_wildcard():
    wildcard = assess_resolution("* * * * *")
    stepped = assess_resolution("*/30 * * * *")
    assert stepped.score < wildcard.score


def test_list_minute_raises_score_vs_single():
    single = assess_resolution("0 * * * *")
    listed = assess_resolution("0,15,30,45 * * * *")
    assert listed.score > single.score


def test_range_minute_partial_score():
    r = assess_resolution("0-29 * * * *")
    s = r.scores["minute"]
    assert 0.0 < s < 1.0


def test_field_resolution_wildcard_is_one():
    assert _field_resolution("*", 59) == 1.0


def test_field_resolution_exact_is_low():
    assert _field_resolution("5", 59) == 0.1


def test_field_resolution_step_decreases_with_larger_step():
    small = _field_resolution("*/2", 59)
    large = _field_resolution("*/30", 59)
    assert small > large


def test_grade_thresholds():
    assert _grade(0.90) == "atomic"
    assert _grade(0.70) == "fine"
    assert _grade(0.50) == "moderate"
    assert _grade(0.30) == "coarse"
    assert _grade(0.10) == "blunt"


def test_batch_resolution_returns_list():
    results = batch_resolution(["* * * * *", "0 9 * * 1", "bad"])
    assert len(results) == 3
    assert all(isinstance(r, ResolutionResult) for r in results)


def test_batch_resolution_handles_invalid():
    results = batch_resolution(["not valid"])
    assert results[0].error is not None


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 0 * * *", "*/15 */6 * * *", "30 12 15 6 3"]:
        r = assess_resolution(expr)
        assert 0.0 <= r.score <= 1.0


def test_str_representation_no_error():
    r = assess_resolution("* * * * *")
    s = str(r)
    assert "ResolutionResult" in s
    assert "score" in s


def test_str_representation_with_error():
    r = assess_resolution("invalid")
    s = str(r)
    assert "error" in s.lower()
