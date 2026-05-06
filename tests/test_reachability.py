"""Tests for crontab_buddy.reachability."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from crontab_buddy.reachability import (
    ReachabilityResult,
    batch_reachability,
    check_reachability,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FUTURE_START = datetime(2030, 1, 1, 0, 0)
FUTURE_END = datetime(2030, 12, 31, 23, 59)


# ---------------------------------------------------------------------------
# check_reachability
# ---------------------------------------------------------------------------

def test_every_minute_is_reachable():
    r = check_reachability("* * * * *", window_days=1)
    assert r.reachable is True


def test_every_minute_has_next_occurrences():
    r = check_reachability("* * * * *", window_days=1)
    assert len(r.next_occurrences) >= 1


def test_invalid_expression_not_reachable():
    r = check_reachability("99 99 99 99 99")
    assert r.reachable is False
    assert r.error is not None


def test_invalid_expression_has_error_message():
    r = check_reachability("not a cron")
    assert "invalid" in r.reason.lower() or r.error


def test_bool_true_when_reachable():
    r = check_reachability("* * * * *", window_days=1)
    assert bool(r) is True


def test_bool_false_when_unreachable():
    r = check_reachability("99 99 99 99 99")
    assert bool(r) is False


def test_str_contains_expression():
    r = check_reachability("0 9 * * 1")
    assert "0 9 * * 1" in str(r)


def test_str_contains_status_reachable():
    r = check_reachability("* * * * *", window_days=1)
    assert "REACHABLE" in str(r)


def test_str_contains_status_unreachable():
    r = check_reachability("99 99 99 99 99")
    assert "UNREACHABLE" in str(r)


def test_custom_window_start_end():
    start = datetime.utcnow()
    end = start + timedelta(hours=2)
    r = check_reachability("* * * * *", start=start, end=end)
    assert r.reachable is True


def test_zero_window_no_occurrences():
    start = datetime(2030, 6, 15, 12, 0)
    end = datetime(2030, 6, 15, 12, 0)  # same moment — nothing can fire
    r = check_reachability("30 12 15 6 *", start=start, end=end)
    # end == start so no full minute passes; expect unreachable
    assert isinstance(r, ReachabilityResult)


# ---------------------------------------------------------------------------
# batch_reachability
# ---------------------------------------------------------------------------

def test_batch_returns_list():
    results = batch_reachability(["* * * * *", "0 0 * * *"])
    assert isinstance(results, list)
    assert len(results) == 2


def test_batch_preserves_order():
    exprs = ["* * * * *", "0 9 * * 1", "invalid"]
    results = batch_reachability(exprs)
    for r, e in zip(results, exprs):
        assert r.expression == e


def test_batch_invalid_expression_in_list():
    results = batch_reachability(["* * * * *", "bad expr"])
    assert results[0].reachable is True
    assert results[1].reachable is False
