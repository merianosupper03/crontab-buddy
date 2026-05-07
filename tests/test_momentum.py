"""Tests for crontab_buddy.momentum."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest

from crontab_buddy.momentum import (
    MomentumResult,
    _level,
    compute_momentum,
    batch_momentum,
)


EXPR = "0 9 * * 1"


def _make_entry(expression: str, days_ago: int = 0) -> dict:
    ts = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return {"expression": expression, "timestamp": ts.isoformat()}


# --- _level ---

def test_level_idle():
    assert _level(0.0) == "idle"
    assert _level(0.1) == "idle"


def test_level_fading():
    assert _level(0.2) == "fading"
    assert _level(0.35) == "fading"


def test_level_steady():
    assert _level(0.4) == "steady"
    assert _level(0.55) == "steady"


def test_level_strong():
    assert _level(0.6) == "strong"
    assert _level(0.75) == "strong"


def test_level_surging():
    assert _level(0.8) == "surging"
    assert _level(1.0) == "surging"


# --- compute_momentum ---

def test_no_history_returns_idle():
    with patch("crontab_buddy.momentum.get_history", return_value=[]):
        result = compute_momentum(EXPR)
    assert result.total_uses == 0
    assert result.recent_uses == 0
    assert result.score == 0.0
    assert result.level == "idle"


def test_returns_momentum_result():
    with patch("crontab_buddy.momentum.get_history", return_value=[]):
        result = compute_momentum(EXPR)
    assert isinstance(result, MomentumResult)


def test_recent_uses_counted():
    history = [_make_entry(EXPR, days_ago=1) for _ in range(5)]
    with patch("crontab_buddy.momentum.get_history", return_value=history):
        result = compute_momentum(EXPR)
    assert result.recent_uses == 5
    assert result.total_uses == 5


def test_old_uses_not_counted_as_recent():
    history = [_make_entry(EXPR, days_ago=10) for _ in range(5)]
    with patch("crontab_buddy.momentum.get_history", return_value=history):
        result = compute_momentum(EXPR)
    assert result.total_uses == 5
    assert result.recent_uses == 0


def test_mixed_history_splits_correctly():
    recent = [_make_entry(EXPR, days_ago=2) for _ in range(3)]
    old = [_make_entry(EXPR, days_ago=20) for _ in range(7)]
    with patch("crontab_buddy.momentum.get_history", return_value=recent + old):
        result = compute_momentum(EXPR)
    assert result.total_uses == 10
    assert result.recent_uses == 3


def test_score_between_zero_and_one():
    history = [_make_entry(EXPR, days_ago=i % 5) for i in range(15)]
    with patch("crontab_buddy.momentum.get_history", return_value=history):
        result = compute_momentum(EXPR)
    assert 0.0 <= result.score <= 1.0


def test_other_expressions_ignored():
    history = [_make_entry("*/5 * * * *", days_ago=1) for _ in range(10)]
    with patch("crontab_buddy.momentum.get_history", return_value=history):
        result = compute_momentum(EXPR)
    assert result.total_uses == 0


def test_str_output_contains_expression():
    with patch("crontab_buddy.momentum.get_history", return_value=[]):
        result = compute_momentum(EXPR)
    assert EXPR in str(result)


# --- batch_momentum ---

def test_batch_returns_list():
    with patch("crontab_buddy.momentum.get_history", return_value=[]):
        results = batch_momentum([EXPR, "*/5 * * * *"])
    assert isinstance(results, list)
    assert len(results) == 2


def test_batch_sorted_by_score_descending():
    history = [_make_entry(EXPR, days_ago=1) for _ in range(15)]
    with patch("crontab_buddy.momentum.get_history", return_value=history):
        results = batch_momentum([EXPR, "*/5 * * * *"])
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)
