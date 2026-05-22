"""Tests for crontab_buddy.opacity"""
import pytest
from crontab_buddy.opacity import assess_opacity, batch_opacity, OpacityResult


def test_returns_opacity_result():
    result = assess_opacity("* * * * *")
    assert isinstance(result, OpacityResult)


def test_all_wildcards_is_transparent():
    result = assess_opacity("* * * * *")
    assert result.grade == "transparent"
    assert result.score >= 0.85


def test_invalid_expression_has_error():
    result = assess_opacity("not valid")
    assert result.error is not None
    assert result.grade == "opaque"


def test_single_exact_time_is_opaque_or_murky():
    result = assess_opacity("30 14 * * *")
    assert result.grade in ("opaque", "murky", "hazy")


def test_scores_dict_has_five_keys():
    result = assess_opacity("0 0 * * 1")
    assert set(result.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 0 * * *", "*/5 * * * *", "0 12 1 1 0"]:
        result = assess_opacity(expr)
        assert 0.0 <= result.score <= 1.0


def test_wildcard_field_opacity_is_one():
    result = assess_opacity("* * * * *")
    for v in result.scores.values():
        assert v == 1.0


def test_exact_field_opacity_is_zero():
    result = assess_opacity("0 0 1 1 0")
    # all fields are exact integers — each should be 0.0
    for v in result.scores.values():
        assert v == 0.0


def test_step_field_raises_score_above_zero():
    result = assess_opacity("*/15 * * * *")
    assert result.scores["minute"] > 0.0


def test_list_field_is_between_zero_and_one():
    result = assess_opacity("0,30 * * * *")
    assert 0.0 < result.scores["minute"] < 1.0


def test_range_field_is_between_zero_and_one():
    result = assess_opacity("0-30 * * * *")
    assert 0.0 <= result.scores["minute"] <= 1.0


def test_str_representation_no_error():
    result = assess_opacity("* * * * *")
    s = str(result)
    assert "OpacityResult" in s
    assert "transparent" in s


def test_str_representation_with_error():
    result = assess_opacity("bad")
    s = str(result)
    assert "error" in s


def test_batch_opacity_returns_list():
    results = batch_opacity(["* * * * *", "0 0 * * *"])
    assert len(results) == 2
    assert all(isinstance(r, OpacityResult) for r in results)


def test_batch_opacity_empty():
    assert batch_opacity([]) == []
