"""Tests for crontab_buddy.trend"""

import json
import os
import tempfile
from datetime import datetime, timedelta

import pytest

from crontab_buddy.trend import compute_trend, format_trend


def _ts(delta_days: int) -> str:
    return (datetime.now() - timedelta(days=delta_days)).isoformat()


def _write_history(path: str, entries):
    with open(path, "w") as f:
        json.dump(entries, f)


@pytest.fixture
def tmp_hist(tmp_path):
    return str(tmp_path / "history.json")


def test_compute_trend_empty(tmp_hist):
    _write_history(tmp_hist, [])
    results = compute_trend(history_path=tmp_hist)
    assert results == []


def test_compute_trend_rising(tmp_hist):
    entries = [
        {"expression": "0 9 * * *", "timestamp": _ts(1)},
        {"expression": "0 9 * * *", "timestamp": _ts(2)},
        {"expression": "0 9 * * *", "timestamp": _ts(10)},
    ]
    _write_history(tmp_hist, entries)
    results = compute_trend(days=7, history_path=tmp_hist)
    assert len(results) == 1
    r = results[0]
    assert r["expression"] == "0 9 * * *"
    assert r["trend"] == "rising"
    assert r["recent_count"] == 2
    assert r["older_count"] == 1
    assert r["trend_score"] == 1


def test_compute_trend_falling(tmp_hist):
    entries = [
        {"expression": "*/5 * * * *", "timestamp": _ts(1)},
        {"expression": "*/5 * * * *", "timestamp": _ts(8)},
        {"expression": "*/5 * * * *", "timestamp": _ts(9)},
    ]
    _write_history(tmp_hist, entries)
    results = compute_trend(days=7, history_path=tmp_hist)
    r = results[0]
    assert r["trend"] == "falling"
    assert r["trend_score"] == -1


def test_compute_trend_stable(tmp_hist):
    entries = [
        {"expression": "0 0 * * 0", "timestamp": _ts(1)},
        {"expression": "0 0 * * 0", "timestamp": _ts(8)},
    ]
    _write_history(tmp_hist, entries)
    results = compute_trend(days=7, history_path=tmp_hist)
    r = results[0]
    assert r["trend"] == "stable"
    assert r["trend_score"] == 0


def test_compute_trend_sorted_by_score(tmp_hist):
    entries = [
        {"expression": "0 1 * * *", "timestamp": _ts(1)},
        {"expression": "0 2 * * *", "timestamp": _ts(1)},
        {"expression": "0 2 * * *", "timestamp": _ts(2)},
        {"expression": "0 3 * * *", "timestamp": _ts(10)},
    ]
    _write_history(tmp_hist, entries)
    results = compute_trend(days=7, history_path=tmp_hist)
    scores = [r["trend_score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_format_trend_no_data():
    assert "No trend data" in format_trend([])


def test_format_trend_contains_expression(tmp_hist):
    entries = [{"expression": "0 6 * * *", "timestamp": _ts(1)}]
    _write_history(tmp_hist, entries)
    results = compute_trend(days=7, history_path=tmp_hist)
    output = format_trend(results)
    assert "0 6 * * *" in output
    assert "RISING" in output or "STABLE" in output or "FALLING" in output
