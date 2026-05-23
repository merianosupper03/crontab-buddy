"""Tests for crontab_buddy.noise."""

import pytest

from crontab_buddy.noise import NoiseResult, assess_noise, batch_noise, _field_noise, _grade


# ---------------------------------------------------------------------------
# _grade helper
# ---------------------------------------------------------------------------

def test_grade_silent():
    assert _grade(0.0) == "silent"


def test_grade_whisper():
    assert _grade(0.15) == "whisper"


def test_grade_deafening():
    assert _grade(0.90) == "deafening"


# ---------------------------------------------------------------------------
# _field_noise helper
# ---------------------------------------------------------------------------

def test_field_wildcard_is_noisy():
    assert _field_noise("*") == 0.6


def test_field_plain_integer_is_silent():
    assert _field_noise("5") == 0.0


def test_field_list_raises_noise():
    score = _field_noise("1,2,3")
    assert score > 0.4


def test_field_step_star_moderate():
    score = _field_noise("*/5")
    assert 0.0 <= score <= 0.6


def test_field_range_moderate():
    score = _field_noise("8-17")
    assert 0.0 < score < 0.6


# ---------------------------------------------------------------------------
# assess_noise
# ---------------------------------------------------------------------------

def test_returns_noise_result():
    result = assess_noise("0 9 * * 1")
    assert isinstance(result, NoiseResult)


def test_invalid_expression_has_error():
    result = assess_noise("invalid")
    assert result.error is not None
    assert result.score == 0.0


def test_all_wildcards_is_loud_or_deafening():
    result = assess_noise("* * * * *")
    assert result.grade in ("loud", "deafening", "moderate")
    assert result.score > 0.4


def test_specific_time_is_quiet():
    result = assess_noise("30 6 * * 1")
    assert result.score < 0.5


def test_scores_dict_has_five_keys():
    result = assess_noise("0 0 1 1 *")
    assert set(result.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 0 1 1 0", "*/5 * * * *", "0,30 9-17 * * 1-5"]:
        result = assess_noise(expr)
        assert 0.0 <= result.score <= 1.0, f"Out of range for {expr!r}: {result.score}"


def test_every_minute_noisier_than_daily():
    every_min = assess_noise("* * * * *")
    daily = assess_noise("0 8 * * *")
    assert every_min.score >= daily.score


def test_str_representation():
    result = assess_noise("0 12 * * *")
    s = str(result)
    assert "NoiseResult" in s
    assert "0 12 * * *" in s


def test_str_representation_error():
    result = assess_noise("bad expr")
    s = str(result)
    assert "error" in s


# ---------------------------------------------------------------------------
# batch_noise
# ---------------------------------------------------------------------------

def test_batch_noise_returns_list():
    results = batch_noise(["* * * * *", "0 9 * * 1"])
    assert isinstance(results, list)
    assert len(results) == 2


def test_batch_noise_each_is_result():
    results = batch_noise(["*/15 * * * *", "0 0 1 * *"])
    for r in results:
        assert isinstance(r, NoiseResult)
