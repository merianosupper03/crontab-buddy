"""Tests for crontab_buddy.granularity."""

import pytest
from crontab_buddy.granularity import assess_granularity, GranularityResult, _field_granularity


def test_returns_granularity_result():
    result = assess_granularity("* * * * *")
    assert isinstance(result, GranularityResult)


def test_all_wildcards_is_ultra_fine():
    result = assess_granularity("* * * * *")
    assert result.grade == "ultra-fine"
    assert result.score >= 0.85


def test_invalid_expression_has_error():
    result = assess_granularity("bad expr")
    assert result.error is not None
    assert result.score == 0.0


def test_single_exact_time_is_coarse():
    result = assess_granularity("30 6 1 1 0")
    assert result.grade in ("very coarse", "coarse")
    assert result.score < 0.45


def test_scores_dict_has_five_keys():
    result = assess_granularity("*/5 * * * *")
    assert set(result.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_step_minute_lowers_score_vs_wildcard():
    wildcard = assess_granularity("* * * * *")
    step = assess_granularity("*/30 * * * *")
    assert step.score < wildcard.score


def test_list_minute_raises_score_vs_single():
    single = assess_granularity("0 * * * *")
    listed = assess_granularity("0,15,30,45 * * * *")
    assert listed.score > single.score


def test_range_minute_between_single_and_wildcard():
    single = assess_granularity("0 * * * *")
    ranged = assess_granularity("0-30 * * * *")
    wildcard = assess_granularity("* * * * *")
    assert single.score <= ranged.score <= wildcard.score


def test_field_granularity_wildcard_is_one():
    assert _field_granularity("*", 59) == 1.0


def test_field_granularity_single_value_is_low():
    assert _field_granularity("5", 59) == 0.2


def test_field_granularity_step_star():
    score = _field_granularity("*/2", 59)
    assert 0.0 < score < 1.0


def test_field_granularity_step_one_is_near_one():
    score = _field_granularity("*/1", 59)
    assert score == 1.0


def test_hourly_expression_medium_grade():
    result = assess_granularity("0 * * * *")
    # minute is exact (0.2), hour is wildcard — overall should be medium-ish
    assert 0.0 < result.score < 0.85


def test_str_representation_no_error():
    result = assess_granularity("*/15 * * * *")
    s = str(result)
    assert "GranularityResult" in s
    assert "error" not in s


def test_str_representation_with_error():
    result = assess_granularity("not valid")
    s = str(result)
    assert "error=" in s
