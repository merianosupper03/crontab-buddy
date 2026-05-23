"""Tests for crontab_buddy.pacing."""

import pytest
from crontab_buddy.pacing import assess_pacing, batch_pacing, PacingResult


def test_returns_pacing_result():
    result = assess_pacing("* * * * *")
    assert isinstance(result, PacingResult)


def test_invalid_expression_has_error():
    result = assess_pacing("not a cron")
    assert result.error is not None
    assert result.fires_per_day == 0


def test_every_minute_fires_1440():
    result = assess_pacing("* * * * *")
    assert result.fires_per_day == 1440
    assert result.error is None


def test_every_minute_is_metered_or_steady():
    result = assess_pacing("* * * * *")
    assert result.grade in ("metered", "steady")


def test_every_minute_score_near_one():
    result = assess_pacing("* * * * *")
    assert result.score >= 0.85


def test_single_exact_time_fires_once():
    result = assess_pacing("30 9 * * *")
    assert result.fires_per_day == 1


def test_single_exact_time_is_choppy_or_erratic():
    result = assess_pacing("30 9 * * *")
    assert result.grade in ("choppy", "erratic", "uneven")


def test_hourly_fires_24_times():
    result = assess_pacing("0 * * * *")
    assert result.fires_per_day == 24


def test_hourly_has_reasonable_grade():
    result = assess_pacing("0 * * * *")
    assert result.grade in ("metered", "steady")


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 * * * *", "0 9 * * 1", "*/15 * * * *"]:
        r = assess_pacing(expr)
        assert 0.0 <= r.score <= 1.0, f"score out of range for {expr!r}: {r.score}"


def test_hourly_variance_is_non_negative():
    result = assess_pacing("0 * * * *")
    assert result.hourly_variance >= 0.0


def test_batch_pacing_returns_list():
    results = batch_pacing(["* * * * *", "0 9 * * *"])
    assert len(results) == 2
    assert all(isinstance(r, PacingResult) for r in results)


def test_batch_pacing_handles_invalid():
    results = batch_pacing(["* * * * *", "bad expr"])
    assert results[0].error is None
    assert results[1].error is not None


def test_str_representation_no_error():
    result = assess_pacing("0 * * * *")
    s = str(result)
    assert "PacingResult" in s
    assert "grade" in s


def test_str_representation_with_error():
    result = assess_pacing("bad")
    s = str(result)
    assert "error" in s
