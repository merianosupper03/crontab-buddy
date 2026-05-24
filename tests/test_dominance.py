"""Tests for crontab_buddy.dominance."""

import pytest
from crontab_buddy.dominance import assess_dominance, batch_dominance, DominanceResult


def test_returns_dominance_result():
    result = assess_dominance("* * * * *")
    assert isinstance(result, DominanceResult)


def test_invalid_expression_has_error():
    result = assess_dominance("not valid")
    assert result.error is not None
    assert result.score == 0.0
    assert result.grade == "negligible"


def test_every_minute_is_overwhelming():
    result = assess_dominance("* * * * *")
    assert result.grade == "overwhelming"


def test_every_minute_score_is_one():
    result = assess_dominance("* * * * *")
    assert result.score == 1.0


def test_every_minute_fires_1440_per_day():
    result = assess_dominance("* * * * *")
    assert result.fires_per_day == 1440


def test_hourly_fires_24_per_day():
    result = assess_dominance("0 * * * *")
    assert result.fires_per_day == 24


def test_daily_fires_once_per_day():
    result = assess_dominance("0 0 * * *")
    assert result.fires_per_day == 1


def test_daily_grade_is_negligible_or_minor():
    result = assess_dominance("0 0 * * *")
    assert result.grade in ("negligible", "minor")


def test_step_minute_every_5():
    result = assess_dominance("*/5 * * * *")
    assert result.fires_per_day == 12 * 24


def test_score_between_zero_and_one():
    for expr in ["0 9 * * 1", "*/15 * * * *", "0 12 * * *"]:
        result = assess_dominance(expr)
        assert 0.0 <= result.score <= 1.0


def test_grade_not_empty():
    result = assess_dominance("0 * * * *")
    assert result.grade
    assert isinstance(result.grade, str)


def test_batch_returns_list():
    results = batch_dominance(["* * * * *", "0 0 * * *"])
    assert isinstance(results, list)
    assert len(results) == 2


def test_batch_preserves_order():
    exprs = ["* * * * *", "0 0 * * *", "*/30 * * * *"]
    results = batch_dominance(exprs)
    for r, e in zip(results, exprs):
        assert r.expression == e


def test_str_no_error():
    result = assess_dominance("0 9 * * 1")
    s = str(result)
    assert "DominanceResult" in s
    assert "score" in s


def test_str_with_error():
    result = assess_dominance("bad expr")
    s = str(result)
    assert "error" in s.lower()
