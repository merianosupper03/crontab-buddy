"""Tests for crontab_buddy.persistence."""
import pytest
from crontab_buddy.persistence import (
    assess_persistence,
    batch_persistence,
    PersistenceResult,
)


def test_returns_persistence_result():
    r = assess_persistence("0 9 * * 1")
    assert isinstance(r, PersistenceResult)


def test_invalid_expression_has_error():
    r = assess_persistence("invalid")
    assert r.error is not None
    assert r.score == 0.0
    assert r.grade == "volatile"


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 * * * *", "0 9 * * *", "0 9 * * 1"]:
        r = assess_persistence(expr)
        assert 0.0 <= r.score <= 1.0, f"score out of range for {expr!r}: {r.score}"


def test_every_minute_has_low_persistence():
    r = assess_persistence("* * * * *")
    assert r.score < 0.3


def test_daily_expression_has_higher_score_than_every_minute():
    daily = assess_persistence("0 9 * * *")
    every_min = assess_persistence("* * * * *")
    assert daily.score > every_min.score


def test_weekly_has_high_persistence():
    r = assess_persistence("0 9 * * 1")
    assert r.score >= 0.5


def test_grade_is_string():
    r = assess_persistence("0 0 * * *")
    assert isinstance(r.grade, str)
    assert len(r.grade) > 0


def test_interval_seconds_populated_for_valid():
    r = assess_persistence("0 * * * *")
    assert r.interval_seconds is not None
    assert r.interval_seconds > 0


def test_interval_seconds_none_for_invalid():
    r = assess_persistence("bad expr")
    assert r.interval_seconds is None


def test_batch_returns_list():
    results = batch_persistence(["* * * * *", "0 9 * * *"])
    assert len(results) == 2
    assert all(isinstance(r, PersistenceResult) for r in results)


def test_batch_handles_invalid():
    results = batch_persistence(["* * * * *", "not valid"])
    assert results[0].error is None
    assert results[1].error is not None


def test_str_representation_valid():
    r = assess_persistence("0 9 * * *")
    s = str(r)
    assert "score" in s
    assert "grade" in s


def test_str_representation_invalid():
    r = assess_persistence("garbage")
    s = str(r)
    assert "error" in s
