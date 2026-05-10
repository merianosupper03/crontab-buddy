"""Tests for crontab_buddy.bandwidth."""

import pytest
from crontab_buddy.bandwidth import assess_bandwidth, batch_bandwidth, BandwidthResult


def test_returns_bandwidth_result():
    result = assess_bandwidth("* * * * *")
    assert isinstance(result, BandwidthResult)


def test_every_minute_is_saturated():
    result = assess_bandwidth("* * * * *")
    assert result.grade == "saturated"


def test_every_minute_score_near_one():
    result = assess_bandwidth("* * * * *")
    assert result.score == pytest.approx(1.0)


def test_every_minute_runs_per_hour():
    result = assess_bandwidth("* * * * *")
    assert result.runs_per_hour == pytest.approx(60.0, rel=0.01)


def test_every_minute_runs_per_day():
    result = assess_bandwidth("* * * * *")
    assert result.runs_per_day == pytest.approx(1440.0, rel=0.01)


def test_hourly_is_light_or_minimal():
    result = assess_bandwidth("0 * * * *")
    assert result.grade in ("minimal", "light")


def test_daily_is_minimal():
    result = assess_bandwidth("0 9 * * *")
    assert result.grade == "minimal"


def test_daily_runs_per_day_is_one():
    result = assess_bandwidth("0 9 * * *")
    assert result.runs_per_day == pytest.approx(1.0, rel=0.05)


def test_invalid_expression_returns_error():
    result = assess_bandwidth("not a cron")
    assert result.error is not None
    assert result.score == 0.0


def test_invalid_expression_grade_is_minimal():
    result = assess_bandwidth("99 99 99 99 99")
    assert result.error is not None
    assert result.grade == "minimal"


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 * * * *", "0 0 * * *", "0 0 * * 0"]:
        r = assess_bandwidth(expr)
        assert 0.0 <= r.score <= 1.0, f"score out of range for {expr!r}"


def test_batch_returns_list():
    results = batch_bandwidth(["* * * * *", "0 9 * * *"])
    assert isinstance(results, list)
    assert len(results) == 2


def test_batch_preserves_order():
    exprs = ["0 9 * * *", "* * * * *", "0 0 1 * *"]
    results = batch_bandwidth(exprs)
    for r, e in zip(results, exprs):
        assert r.expression == e


def test_str_with_error():
    r = assess_bandwidth("bad expr")
    assert "error" in str(r).lower()


def test_str_without_error():
    r = assess_bandwidth("0 9 * * *")
    s = str(r)
    assert "0 9 * * *" in s
    assert "grade" in s
