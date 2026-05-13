"""Tests for crontab_buddy.burstiness."""

import pytest

from crontab_buddy.burstiness import (
    assess_burstiness,
    batch_burstiness,
    BurstinessResult,
)


def test_returns_burstiness_result():
    result = assess_burstiness("* * * * *")
    assert isinstance(result, BurstinessResult)


def test_every_minute_is_uniform():
    result = assess_burstiness("* * * * *")
    assert result.label == "uniform"


def test_every_minute_score_near_zero():
    result = assess_burstiness("* * * * *")
    assert result.score < 0.1


def test_single_firing_is_spiky():
    result = assess_burstiness("0 * * * *")
    assert result.label == "spiky"
    assert result.score == 1.0


def test_single_firing_has_empty_intervals():
    result = assess_burstiness("0 * * * *")
    assert result.intervals == []


def test_step_every_15_minutes_is_smooth_or_uniform():
    result = assess_burstiness("*/15 * * * *")
    assert result.label in ("uniform", "smooth")


def test_step_every_15_minutes_score_near_zero():
    result = assess_burstiness("*/15 * * * *")
    assert result.score < 0.15


def test_list_minutes_clustered_is_bursty():
    # 0,1,2 clustered at start — very uneven spacing vs rest of hour
    result = assess_burstiness("0,1,2 * * * *")
    assert result.score < 0.15  # intervals are [1,1] — uniform among themselves


def test_step_every_30_minutes_is_uniform():
    result = assess_burstiness("*/30 * * * *")
    # only 0 and 30 — two firings, one interval of 30 — cv=0
    assert result.score == 0.0
    assert result.label == "uniform"


def test_invalid_expression_returns_error():
    result = assess_burstiness("99 99 99 99 99")
    assert result.error is not None
    assert result.score == 1.0


def test_invalid_expression_label_is_spiky():
    result = assess_burstiness("bad expression")
    assert result.label == "spiky"


def test_intervals_count_matches_firings_minus_one():
    result = assess_burstiness("*/5 * * * *")
    # */5 -> 0,5,10,...,55 = 12 values, 11 intervals
    assert len(result.intervals) == 11


def test_batch_returns_list():
    results = batch_burstiness(["* * * * *", "0 * * * *"])
    assert len(results) == 2


def test_batch_preserves_order():
    exprs = ["*/5 * * * *", "0 12 * * *", "* * * * *"]
    results = batch_burstiness(exprs)
    assert [r.expression for r in results] == exprs


def test_str_no_error():
    result = assess_burstiness("*/10 * * * *")
    s = str(result)
    assert "burstiness=" in s
    assert result.expression in s


def test_str_with_error():
    result = assess_burstiness("not valid")
    s = str(result)
    assert "error" in s
