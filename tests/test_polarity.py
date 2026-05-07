"""Tests for crontab_buddy.polarity."""

import pytest
from crontab_buddy.polarity import assess_polarity, batch_polarity, PolarityResult


def test_returns_polarity_result():
    result = assess_polarity("0 12 * * *")
    assert isinstance(result, PolarityResult)


def test_invalid_expression_returns_error():
    result = assess_polarity("not valid")
    assert result.polarity == "error"
    assert result.error is not None


def test_noon_is_daytime():
    result = assess_polarity("0 12 * * *")
    assert result.polarity == "daytime"
    assert result.score > 0


def test_midnight_is_nighttime():
    result = assess_polarity("0 2 * * *")
    assert result.polarity == "nighttime"
    assert result.score < 0


def test_all_hours_wildcard_is_neutral_or_all_day():
    result = assess_polarity("* * * * *")
    # wildcard covers all hours; day=14, night=10, score > 0 slightly
    assert result.day_hours == 14
    assert result.night_hours == 10
    assert result.polarity in ("daytime", "neutral")


def test_step_every_two_hours_has_mixed_hours():
    result = assess_polarity("0 */2 * * *")
    assert result.day_hours > 0
    assert result.night_hours > 0


def test_range_hour_daytime():
    # hours 8-17 are all daytime
    result = assess_polarity("0 8-17 * * *")
    assert result.polarity == "daytime"
    assert result.score > 0.5


def test_list_hour_nighttime():
    result = assess_polarity("0 1,3,22 * * *")
    assert result.polarity == "nighttime"
    assert result.score < 0


def test_score_between_minus_one_and_one():
    for expr in ["* * * * *", "0 9 * * *", "0 23 * * *", "0 */3 * * *"]:
        r = assess_polarity(expr)
        if not r.error:
            assert -1.0 <= r.score <= 1.0


def test_str_representation_no_error():
    result = assess_polarity("0 10 * * *")
    s = str(result)
    assert "0 10 * * *" in s
    assert "day=" in s


def test_str_representation_error():
    result = assess_polarity("bad")
    s = str(result)
    assert "error" in s


def test_batch_polarity_returns_list():
    results = batch_polarity(["0 9 * * *", "0 2 * * *"])
    assert len(results) == 2
    assert all(isinstance(r, PolarityResult) for r in results)


def test_batch_polarity_preserves_order():
    exprs = ["0 9 * * *", "0 2 * * *", "* * * * *"]
    results = batch_polarity(exprs)
    for i, r in enumerate(results):
        assert r.expression == exprs[i]


def test_day_hours_plus_night_hours_equals_active():
    result = assess_polarity("0 */4 * * *")
    assert result.day_hours + result.night_hours == 6  # 0,4,8,12,16,20
