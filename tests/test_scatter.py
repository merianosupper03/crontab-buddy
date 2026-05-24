"""Tests for crontab_buddy.scatter."""
import pytest
from crontab_buddy.scatter import assess_scatter, batch_scatter, ScatterResult


def test_returns_scatter_result():
    result = assess_scatter("* * * * *")
    assert isinstance(result, ScatterResult)


def test_invalid_expression_has_error():
    result = assess_scatter("99 * * * *")
    assert result.error is not None
    assert result.score == 0.0


def test_every_minute_is_diffuse_or_spread():
    result = assess_scatter("* * * * *")
    assert result.error is None
    assert result.grade in ("diffuse", "spread")


def test_every_minute_fires_60_times():
    result = assess_scatter("* * * * *")
    assert len(result.firing_minutes) == 60


def test_every_minute_spread_is_59():
    result = assess_scatter("* * * * *")
    assert result.spread == 59.0


def test_single_exact_minute_is_concentrated():
    result = assess_scatter("30 * * * *")
    assert result.grade == "concentrated"
    assert result.score == 0.0
    assert result.spread == 0.0


def test_single_minute_has_one_firing_point():
    result = assess_scatter("15 * * * *")
    assert result.firing_minutes == [15]


def test_step_every_15_minutes():
    result = assess_scatter("*/15 * * * *")
    assert 0 in result.firing_minutes
    assert 15 in result.firing_minutes
    assert 30 in result.firing_minutes
    assert 45 in result.firing_minutes
    assert len(result.firing_minutes) == 4


def test_step_every_15_has_positive_spread():
    result = assess_scatter("*/15 * * * *")
    assert result.spread == 45.0


def test_range_minute():
    result = assess_scatter("10-20 * * * *")
    assert result.firing_minutes == list(range(10, 21))
    assert result.spread == 10.0


def test_list_minute():
    result = assess_scatter("0,20,40 * * * *")
    assert result.firing_minutes == [0, 20, 40]
    assert result.spread == 40.0


def test_score_between_zero_and_one():
    for expr in ("* * * * *", "*/5 * * * *", "0 * * * *", "0,30 * * * *"):
        r = assess_scatter(expr)
        if not r.error:
            assert 0.0 <= r.score <= 1.0


def test_batch_returns_list():
    results = batch_scatter(["* * * * *", "0 * * * *", "*/10 * * * *"])
    assert len(results) == 3
    assert all(isinstance(r, ScatterResult) for r in results)


def test_batch_handles_invalid():
    results = batch_scatter(["* * * * *", "99 * * * *"])
    assert results[0].error is None
    assert results[1].error is not None


def test_str_no_error():
    result = assess_scatter("*/5 * * * *")
    s = str(result)
    assert "Scatter" in s
    assert "grade=" in s


def test_str_with_error():
    result = assess_scatter("bad expression")
    s = str(result)
    assert "error=" in s
