"""Tests for crontab_buddy.churn"""
import pytest
from crontab_buddy.churn import assess_churn, batch_churn, ChurnResult


EVERY_MINUTE = "* * * * *"
HOURLY = "0 * * * *"
DAILY_NOON = "0 12 * * *"
DAILY_MIDNIGHT = "0 0 * * *"
WEEKLY = "0 9 * * 1"


def test_returns_churn_result():
    result = assess_churn(EVERY_MINUTE, [])
    assert isinstance(result, ChurnResult)


def test_invalid_expression_has_error():
    result = assess_churn("not a cron", [])
    assert result.error is not None
    assert "Invalid" in result.error


def test_no_peers_gives_stable_score():
    result = assess_churn(DAILY_NOON, [])
    assert result.error is None
    assert result.score == 0.0
    assert result.grade == "stable"


def test_identical_peer_is_excluded():
    # Self-matches should not count as peers
    result = assess_churn(DAILY_NOON, [DAILY_NOON, DAILY_NOON])
    assert result.unique_peers == 0
    assert result.score == 0.0


def test_non_overlapping_peer_zero_overlap():
    # DAILY_NOON fires at 12:00; DAILY_MIDNIGHT fires at 00:00 — no overlap
    result = assess_churn(DAILY_NOON, [DAILY_MIDNIGHT])
    assert result.unique_peers == 1
    assert result.overlapping_peers == 0
    assert result.score == 0.0
    assert result.grade == "stable"


def test_overlapping_peer_increases_score():
    # EVERY_MINUTE overlaps with HOURLY (minute 0 of every hour)
    result = assess_churn(EVERY_MINUTE, [HOURLY])
    assert result.unique_peers == 1
    assert result.overlapping_peers == 1
    assert result.score == 1.0


def test_partial_overlap():
    # HOURLY overlaps with DAILY_NOON (both fire at 12:00)
    result = assess_churn(HOURLY, [DAILY_NOON, DAILY_MIDNIGHT])
    assert result.unique_peers == 2
    assert result.overlapping_peers == 2  # hourly fires at every hour including 0 and 12
    assert result.score == 1.0


def test_score_between_zero_and_one():
    result = assess_churn(HOURLY, [DAILY_NOON, WEEKLY])
    assert 0.0 <= result.score <= 1.0


def test_grade_values_are_valid():
    valid_grades = {"stable", "drifting", "shifting", "volatile", "turbulent"}
    result = assess_churn(EVERY_MINUTE, [HOURLY, DAILY_NOON, DAILY_MIDNIGHT, WEEKLY])
    assert result.grade in valid_grades


def test_duplicate_peers_counted_once():
    # Two identical peers should be deduplicated
    result = assess_churn(DAILY_NOON, [HOURLY, HOURLY])
    assert result.unique_peers == 1


def test_invalid_peer_is_skipped():
    result = assess_churn(DAILY_NOON, ["bad expr", HOURLY])
    assert result.unique_peers == 1  # only HOURLY is valid


def test_batch_churn_returns_list():
    expressions = [EVERY_MINUTE, HOURLY, DAILY_NOON]
    results = batch_churn(expressions)
    assert len(results) == 3
    assert all(isinstance(r, ChurnResult) for r in results)


def test_batch_churn_uses_others_as_peers():
    expressions = [DAILY_NOON, DAILY_MIDNIGHT, WEEKLY]
    results = batch_churn(expressions)
    # Each expression is assessed against the other two
    for r in results:
        assert r.unique_peers <= 2


def test_every_minute_vs_many_peers_is_turbulent_or_volatile():
    peers = [HOURLY, DAILY_NOON, DAILY_MIDNIGHT, WEEKLY, "*/5 * * * *"]
    result = assess_churn(EVERY_MINUTE, peers)
    # every minute overlaps with all peers
    assert result.grade in {"turbulent", "volatile", "shifting"}
    assert result.score > 0.0
