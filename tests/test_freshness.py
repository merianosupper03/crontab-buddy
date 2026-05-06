"""Tests for crontab_buddy.freshness."""

from datetime import datetime, timedelta, timezone

import pytest

from crontab_buddy.freshness import (
    FreshnessResult,
    assess_freshness,
    batch_freshness,
)


def _days_ago(n: float) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=n)


def test_no_last_seen_is_unknown():
    r = assess_freshness("0 * * * *")
    assert r.label == "unknown"
    assert r.score == 0.0
    assert r.last_seen is None
    assert r.days_since is None


def test_very_recent_is_fresh():
    r = assess_freshness("0 * * * *", _days_ago(0.5))
    assert r.label == "fresh"
    assert r.score == 1.0


def test_within_seven_days_is_recent():
    r = assess_freshness("0 * * * *", _days_ago(4))
    assert r.label == "recent"
    assert r.score == 0.75


def test_within_thirty_days_is_aging():
    r = assess_freshness("0 * * * *", _days_ago(15))
    assert r.label == "aging"
    assert r.score == 0.50


def test_within_ninety_days_is_stale():
    r = assess_freshness("0 * * * *", _days_ago(60))
    assert r.label == "stale"
    assert r.score == 0.25


def test_beyond_ninety_days_is_expired():
    r = assess_freshness("0 * * * *", _days_ago(120))
    assert r.label == "expired"
    assert r.score == 0.0


def test_days_since_is_approximate():
    r = assess_freshness("* * * * *", _days_ago(3))
    assert r.days_since is not None
    assert 2.9 < r.days_since < 3.1


def test_str_with_last_seen():
    r = assess_freshness("0 0 * * *", _days_ago(0.1))
    s = str(r)
    assert "0 0 * * *" in s
    assert "fresh" in s
    assert "score" in s


def test_str_without_last_seen():
    r = assess_freshness("0 0 * * *")
    s = str(r)
    assert "never seen" in s


def test_naive_datetime_treated_as_utc():
    naive = datetime.utcnow() - timedelta(hours=2)
    r = assess_freshness("* * * * *", naive)
    assert r.label == "fresh"


def test_batch_freshness_returns_all():
    entries = [
        ("* * * * *", _days_ago(0)),
        ("0 0 * * *", _days_ago(50)),
        ("0 12 * * 1", None),
    ]
    results = batch_freshness(entries)
    assert len(results) == 3
    assert results[0].label == "fresh"
    assert results[1].label == "stale"
    assert results[2].label == "unknown"


def test_batch_freshness_returns_freshness_result_instances():
    entries = [("* * * * *", _days_ago(1))]
    results = batch_freshness(entries)
    assert all(isinstance(r, FreshnessResult) for r in results)


def test_exactly_one_day_is_fresh():
    r = assess_freshness("0 * * * *", _days_ago(1))
    assert r.label == "fresh"
