"""Tests for crontab_buddy.drift."""

from datetime import datetime, timedelta
import pytest
from unittest.mock import patch
from crontab_buddy.drift import detect_drift, drift_summary, DriftResult


FIXED_BASE = datetime(2024, 1, 15, 12, 0, 0)


def _runs(expr, count=10, start=None):
    """Return a predictable list of datetimes for mocking next_runs."""
    base = start or FIXED_BASE
    return [base + timedelta(hours=i) for i in range(count)]


def test_detect_drift_no_drift():
    actual = FIXED_BASE
    with patch("crontab_buddy.drift.next_runs", side_effect=_runs):
        result = detect_drift("0 * * * *", actual, reference=FIXED_BASE - timedelta(hours=1))
    assert result.drifted is False
    assert result.delta_seconds == 0


def test_detect_drift_late():
    actual = FIXED_BASE + timedelta(seconds=90)
    with patch("crontab_buddy.drift.next_runs", side_effect=_runs):
        result = detect_drift("0 * * * *", actual, reference=FIXED_BASE - timedelta(hours=1))
    assert result.drifted is True
    assert result.delta_seconds == 90


def test_detect_drift_early():
    actual = FIXED_BASE - timedelta(seconds=45)
    with patch("crontab_buddy.drift.next_runs", side_effect=_runs):
        result = detect_drift("0 * * * *", actual, reference=FIXED_BASE - timedelta(hours=1))
    assert result.drifted is True
    assert result.delta_seconds == -45


def test_detect_drift_invalid_expression():
    with pytest.raises(ValueError, match="Invalid expression"):
        detect_drift("99 99 99 99 99", datetime.now())


def test_detect_drift_no_runs_raises():
    actual = FIXED_BASE
    with patch("crontab_buddy.drift.next_runs", return_value=[]):
        with pytest.raises(ValueError, match="Could not compute"):
            detect_drift("0 * * * *", actual)


def test_drift_result_str_no_drift():
    r = DriftResult("0 * * * *", FIXED_BASE, FIXED_BASE)
    assert "no drift" in str(r)


def test_drift_result_str_late():
    r = DriftResult("0 * * * *", FIXED_BASE, FIXED_BASE + timedelta(seconds=120))
    assert "late" in str(r)
    assert "120" in str(r)


def test_drift_result_str_early():
    r = DriftResult("0 * * * *", FIXED_BASE, FIXED_BASE - timedelta(seconds=30))
    assert "early" in str(r)


def test_drift_summary_all_on_time():
    results = [DriftResult("* * * * *", FIXED_BASE, FIXED_BASE) for _ in range(5)]
    s = drift_summary(results)
    assert s["total"] == 5
    assert s["drifted"] == 0
    assert s["max_drift_seconds"] == 0
    assert s["avg_drift_seconds"] == 0


def test_drift_summary_mixed():
    r1 = DriftResult("* * * * *", FIXED_BASE, FIXED_BASE)
    r2 = DriftResult("* * * * *", FIXED_BASE, FIXED_BASE + timedelta(seconds=60))
    r3 = DriftResult("* * * * *", FIXED_BASE, FIXED_BASE + timedelta(seconds=120))
    s = drift_summary([r1, r2, r3])
    assert s["total"] == 3
    assert s["drifted"] == 2
    assert s["max_drift_seconds"] == 120
    assert s["avg_drift_seconds"] == 90.0
