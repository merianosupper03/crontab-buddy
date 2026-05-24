"""Tests for crontab_buddy.exposure."""

import pytest
from crontab_buddy.exposure import assess_exposure, batch_exposure, ExposureResult


def test_returns_exposure_result():
    result = assess_exposure("* * * * *")
    assert isinstance(result, ExposureResult)


def test_invalid_expression_has_error():
    result = assess_exposure("invalid")
    assert result.error is not None
    assert result.score == 0.0


def test_all_wildcards_is_total():
    result = assess_exposure("* * * * *")
    assert result.grade == "total"
    assert result.score == pytest.approx(1.0)


def test_single_exact_time_is_pinpoint_or_minimal():
    result = assess_exposure("0 9 1 1 1")
    assert result.grade in ("pinpoint", "minimal")
    assert result.score < 0.2


def test_scores_dict_has_five_keys():
    result = assess_exposure("*/5 * * * *")
    assert set(result.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_step_minute_raises_exposure():
    result_step = assess_exposure("*/5 * * * *")
    result_exact = assess_exposure("0 * * * *")
    assert result_step.score > result_exact.score


def test_list_minute_raises_exposure():
    result_list = assess_exposure("0,15,30,45 * * * *")
    result_single = assess_exposure("0 * * * *")
    assert result_list.score > result_single.score


def test_range_minute_raises_exposure():
    result_range = assess_exposure("0-29 * * * *")
    result_single = assess_exposure("0 * * * *")
    assert result_range.score > result_single.score


def test_hourly_is_moderate_or_low():
    result = assess_exposure("0 * * * *")
    assert result.grade in ("moderate", "low", "minimal", "pinpoint")


def test_daily_midnight_is_low_or_minimal():
    result = assess_exposure("0 0 * * *")
    assert result.score < 0.5


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 9 * * 1", "*/15 * * * *", "0 0 1 * *"]:
        result = assess_exposure(expr)
        assert 0.0 <= result.score <= 1.0


def test_batch_returns_list():
    results = batch_exposure(["* * * * *", "0 9 * * 1"])
    assert len(results) == 2
    assert all(isinstance(r, ExposureResult) for r in results)


def test_batch_handles_invalid():
    results = batch_exposure(["bad", "* * * * *"])
    assert results[0].error is not None
    assert results[1].error is None


def test_str_no_error():
    result = assess_exposure("0 12 * * *")
    s = str(result)
    assert "ExposureResult" in s
    assert "score" in s


def test_str_with_error():
    result = assess_exposure("bad expr")
    s = str(result)
    assert "error" in s
