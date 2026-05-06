"""Tests for crontab_buddy.velocity."""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from crontab_buddy.velocity import (
    VelocityResult,
    _level,
    compute_velocity,
    batch_velocity,
    _WINDOWS,
)


# ---------------------------------------------------------------------------
# _level helper
# ---------------------------------------------------------------------------

def test_level_idle():
    assert _level(0) == "idle"


def test_level_low():
    assert _level(0.5) == "low"


def test_level_moderate():
    assert _level(1.0) == "moderate"


def test_level_high():
    assert _level(10.0) == "high"


# ---------------------------------------------------------------------------
# compute_velocity
# ---------------------------------------------------------------------------

def _make_history(expr: str, count: int, ts_offset: int = 0):
    now = time.time()
    return [
        {"expression": expr, "timestamp": now - ts_offset}
        for _ in range(count)
    ]


def test_compute_velocity_returns_result():
    with patch("crontab_buddy.velocity.get_history", return_value=[]):
        r = compute_velocity("* * * * *")
    assert isinstance(r, VelocityResult)


def test_compute_velocity_zero_when_no_history():
    with patch("crontab_buddy.velocity.get_history", return_value=[]):
        r = compute_velocity("0 * * * *", window="24h")
    assert r.count == 0
    assert r.level == "idle"


def test_compute_velocity_counts_matching_entries():
    hist = _make_history("0 * * * *", 5)
    with patch("crontab_buddy.velocity.get_history", return_value=hist):
        r = compute_velocity("0 * * * *", window="24h")
    assert r.count == 5


def test_compute_velocity_ignores_old_entries():
    old = _make_history("0 * * * *", 3, ts_offset=999999)
    with patch("crontab_buddy.velocity.get_history", return_value=old):
        r = compute_velocity("0 * * * *", window="1h")
    assert r.count == 0


def test_compute_velocity_ignores_other_expressions():
    hist = _make_history("*/5 * * * *", 4)
    with patch("crontab_buddy.velocity.get_history", return_value=hist):
        r = compute_velocity("0 * * * *", window="24h")
    assert r.count == 0


def test_compute_velocity_invalid_window_raises():
    with pytest.raises(ValueError, match="Unknown window"):
        compute_velocity("* * * * *", window="99y")


def test_compute_velocity_rate_per_hour():
    hist = _make_history("* * * * *", 24)
    with patch("crontab_buddy.velocity.get_history", return_value=hist):
        r = compute_velocity("* * * * *", window="24h")
    assert r.rate_per_hour == pytest.approx(1.0, rel=1e-3)


def test_compute_velocity_window_stored():
    with patch("crontab_buddy.velocity.get_history", return_value=[]):
        r = compute_velocity("* * * * *", window="7d")
    assert r.window == "7d"


# ---------------------------------------------------------------------------
# batch_velocity
# ---------------------------------------------------------------------------

def test_batch_velocity_returns_list():
    with patch("crontab_buddy.velocity.get_history", return_value=[]):
        results = batch_velocity(["* * * * *", "0 * * * *"])
    assert len(results) == 2


def test_batch_velocity_all_velocity_results():
    with patch("crontab_buddy.velocity.get_history", return_value=[]):
        results = batch_velocity(["* * * * *"])
    assert all(isinstance(r, VelocityResult) for r in results)


# ---------------------------------------------------------------------------
# __str__
# ---------------------------------------------------------------------------

def test_str_contains_expression():
    r = VelocityResult("* * * * *", "24h", 5, 0.208, "low")
    assert "* * * * *" in str(r)


def test_str_contains_level():
    r = VelocityResult("* * * * *", "24h", 0, 0.0, "idle")
    assert "idle" in str(r)
