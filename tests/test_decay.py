"""Tests for crontab_buddy.decay and decay_cli."""

import json
from datetime import datetime, timedelta, timezone

import pytest

from crontab_buddy.decay import (
    DecayResult,
    compute_decay,
    is_stale,
    format_decay,
    _DECAY_HALF_LIVES,
)
from crontab_buddy.decay_cli import cmd_decay_score, cmd_decay_check, cmd_decay_json


EXPR = "0 9 * * 1"
NOW = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)


def _days_ago(n):
    return NOW - timedelta(days=n)


# --- decay logic ---

def test_fresh_expression_score_near_one():
    result = compute_decay(EXPR, _days_ago(0), now=NOW)
    assert result.score > 0.99


def test_score_decreases_over_time():
    r1 = compute_decay(EXPR, _days_ago(10), now=NOW)
    r2 = compute_decay(EXPR, _days_ago(30), now=NOW)
    assert r1.score > r2.score


def test_half_life_normal_at_30_days_is_half():
    result = compute_decay(EXPR, _days_ago(30), half_life="normal", now=NOW)
    assert abs(result.score - 0.5) < 0.001


def test_half_life_fast_at_7_days_is_half():
    result = compute_decay(EXPR, _days_ago(7), half_life="fast", now=NOW)
    assert abs(result.score - 0.5) < 0.001


def test_half_life_slow_at_90_days_is_half():
    result = compute_decay(EXPR, _days_ago(90), half_life="slow", now=NOW)
    assert abs(result.score - 0.5) < 0.001


def test_invalid_half_life_raises():
    with pytest.raises(ValueError, match="Unknown half_life"):
        compute_decay(EXPR, _days_ago(5), half_life="glacial", now=NOW)


def test_is_stale_false_for_fresh():
    result = compute_decay(EXPR, _days_ago(1), now=NOW)
    assert not is_stale(result)


def test_is_stale_true_for_old():
    result = compute_decay(EXPR, _days_ago(200), now=NOW)
    assert is_stale(result)


def test_age_days_stored_correctly():
    result = compute_decay(EXPR, _days_ago(15), now=NOW)
    assert abs(result.age_days - 15.0) < 0.01


def test_format_decay_contains_expression():
    result = compute_decay(EXPR, _days_ago(5), now=NOW)
    text = format_decay(result)
    assert EXPR in text
    assert "score" in text.lower()


# --- CLI ---

class Args:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


def test_cmd_decay_score_prints_score():
    out = []
    args = Args(expression=EXPR, last_used="2024-05-01T12:00:00", half_life="normal")
    cmd_decay_score(args, print_fn=out.append)
    assert any("score" in line.lower() for line in out)


def test_cmd_decay_score_invalid_date_prints_error():
    out = []
    args = Args(expression=EXPR, last_used="not-a-date", half_life="normal")
    cmd_decay_score(args, print_fn=out.append)
    assert any("error" in line.lower() for line in out)


def test_cmd_decay_check_fresh_prints_fresh():
    out = []
    args = Args(expression=EXPR, last_used=NOW.isoformat(), half_life="normal", threshold=0.1)
    cmd_decay_check(args, print_fn=out.append)
    assert any("FRESH" in line for line in out)


def test_cmd_decay_check_stale_prints_stale():
    out = []
    old = (NOW - timedelta(days=300)).isoformat()
    args = Args(expression=EXPR, last_used=old, half_life="normal", threshold=0.1)
    cmd_decay_check(args, print_fn=out.append)
    assert any("STALE" in line for line in out)


def test_cmd_decay_json_outputs_valid_json():
    out = []
    args = Args(expression=EXPR, last_used="2024-05-01T12:00:00", half_life="normal")
    cmd_decay_json(args, print_fn=out.append)
    data = json.loads("\n".join(out))
    assert "score" in data
    assert "stale" in data
    assert data["expression"] == EXPR
