"""Tests for crontab_buddy.inertia."""

import pytest
from crontab_buddy.inertia import assess_inertia, batch_inertia, InertiaResult


def test_returns_inertia_result():
    result = assess_inertia("* * * * *")
    assert isinstance(result, InertiaResult)


def test_invalid_expression_has_error():
    result = assess_inertia("not a cron")
    assert result.error is not None
    assert result.score == 0.0


def test_every_minute_is_fluid():
    result = assess_inertia("* * * * *")
    assert result.error is None
    assert result.grade == "fluid"


def test_every_minute_score_near_zero():
    result = assess_inertia("* * * * *")
    assert result.score < 0.1


def test_weekly_is_resistant_or_immovable():
    result = assess_inertia("0 9 * * 1")
    assert result.error is None
    assert result.grade in ("resistant", "immovable", "moderate")


def test_weekly_score_higher_than_daily():
    weekly = assess_inertia("0 9 * * 1")
    daily = assess_inertia("0 9 * * *")
    assert weekly.score >= daily.score


def test_daily_score_higher_than_hourly():
    daily = assess_inertia("0 9 * * *")
    hourly = assess_inertia("0 * * * *")
    assert daily.score > hourly.score


def test_hourly_score_higher_than_every_minute():
    hourly = assess_inertia("0 * * * *")
    every_minute = assess_inertia("* * * * *")
    assert hourly.score > every_minute.score


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 * * * *", "0 9 * * *", "0 9 * * 1", "0 0 1 * *"]:
        result = assess_inertia(expr)
        if result.error is None:
            assert 0.0 <= result.score <= 1.0


def test_interval_seconds_stored():
    result = assess_inertia("0 * * * *")
    assert result.interval_seconds == 3600


def test_description_contains_grade():
    result = assess_inertia("0 9 * * *")
    assert result.grade in result.description


def test_batch_inertia_returns_list():
    results = batch_inertia(["* * * * *", "0 9 * * *"])
    assert isinstance(results, list)
    assert len(results) == 2


def test_batch_inertia_each_is_result():
    results = batch_inertia(["* * * * *", "0 9 * * *"])
    for r in results:
        assert isinstance(r, InertiaResult)


def test_str_with_error():
    result = assess_inertia("bad")
    s = str(result)
    assert "error" in s.lower()


def test_str_without_error():
    result = assess_inertia("* * * * *")
    s = str(result)
    assert "score" in s.lower()
    assert "grade" in s.lower()
