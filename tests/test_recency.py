"""Tests for crontab_buddy.recency."""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
import pytest
from crontab_buddy.recency import (
    assess_recency,
    batch_recency,
    RecencyResult,
)


def _ago(**kwargs) -> datetime:
    return datetime.now(timezone.utc) - timedelta(**kwargs)


def test_returns_recency_result():
    result = assess_recency("* * * * *")
    assert isinstance(result, RecencyResult)


def test_no_last_seen_is_never_seen():
    result = assess_recency("0 9 * * 1")
    assert result.label == "never seen"
    assert result.score == 0.0
    assert result.minutes_ago is None


def test_very_recent_is_just_now():
    result = assess_recency("*/5 * * * *", last_seen=_ago(seconds=30))
    assert result.label == "just now"
    assert result.score == 1.0


def test_within_one_hour_is_very_recent():
    result = assess_recency("0 * * * *", last_seen=_ago(minutes=45))
    assert result.label == "very recent"
    assert result.score >= 0.8


def test_within_one_day_is_recent():
    result = assess_recency("0 9 * * *", last_seen=_ago(hours=6))
    assert result.label == "recent"
    assert 0.5 <= result.score <= 0.9


def test_within_one_week_is_aging():
    result = assess_recency("0 0 * * 0", last_seen=_ago(days=4))
    assert result.label == "aging"
    assert result.score < 0.7


def test_within_thirty_days_is_old():
    result = assess_recency("0 0 1 * *", last_seen=_ago(days=20))
    assert result.label == "old"
    assert result.score <= 0.4


def test_over_thirty_days_is_ancient():
    result = assess_recency("0 0 1 1 *", last_seen=_ago(days=60))
    assert result.label == "ancient"
    assert result.score <= 0.1


def test_minutes_ago_is_positive():
    result = assess_recency("* * * * *", last_seen=_ago(minutes=10))
    assert result.minutes_ago is not None
    assert result.minutes_ago >= 9.9


def test_naive_datetime_treated_as_utc():
    naive = datetime.utcnow() - timedelta(minutes=5)
    result = assess_recency("*/5 * * * *", last_seen=naive)
    assert result.minutes_ago is not None
    assert result.minutes_ago < 10


def test_future_datetime_clamped_to_zero_minutes():
    future = datetime.now(timezone.utc) + timedelta(hours=1)
    result = assess_recency("0 * * * *", last_seen=future)
    assert result.minutes_ago == 0.0
    assert result.label == "just now"


def test_batch_recency_returns_list():
    entries = [("* * * * *", None), ("0 9 * * *", _ago(hours=2))]
    results = batch_recency(entries)
    assert len(results) == 2
    assert all(isinstance(r, RecencyResult) for r in results)


def test_batch_recency_first_is_never_seen():
    entries = [("* * * * *", None)]
    results = batch_recency(entries)
    assert results[0].label == "never seen"


def test_str_representation_contains_label():
    result = assess_recency("0 0 * * *", last_seen=_ago(days=1))
    assert result.label in str(result)
