"""Tests for crontab_buddy.weight and weight_cli."""

from __future__ import annotations
import json
import pytest
from io import StringIO
from unittest.mock import patch
from crontab_buddy.weight import assess_weight, batch_weight, WeightResult
from crontab_buddy.weight_cli import (
    cmd_weight_check,
    cmd_weight_score,
    cmd_weight_grade,
    cmd_weight_batch,
    cmd_weight_json,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def captured(cmd, **kwargs):
    args = Args(**kwargs)
    buf = StringIO()
    with patch("builtins.print", side_effect=lambda *a, **k: buf.write(" ".join(str(x) for x in a) + "\n")):
        cmd(args)
    return buf.getvalue()


# --- assess_weight ---

def test_returns_weight_result():
    r = assess_weight("* * * * *")
    assert isinstance(r, WeightResult)


def test_invalid_expression_has_error():
    r = assess_weight("bad expr")
    assert r.error is not None
    assert r.score == 0.0


def test_every_minute_is_crushing_or_heavy():
    r = assess_weight("* * * * *")
    assert r.grade in ("heavy", "crushing")


def test_every_minute_score_near_one():
    r = assess_weight("* * * * *")
    assert r.score >= 0.95


def test_every_minute_runs_per_day_is_1440():
    r = assess_weight("* * * * *")
    assert r.runs_per_day == pytest.approx(1440.0, rel=0.01)


def test_daily_is_featherlight_or_light():
    r = assess_weight("0 9 * * *")
    assert r.grade in ("featherlight", "light")


def test_weekly_is_featherlight():
    r = assess_weight("0 0 * * 0")
    assert r.grade == "featherlight"


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 * * * *", "0 0 * * *", "0 0 * * 0"]:
        r = assess_weight(expr)
        assert 0.0 <= r.score <= 1.0


def test_batch_weight_returns_list():
    results = batch_weight(["* * * * *", "0 9 * * *"])
    assert len(results) == 2
    assert all(isinstance(r, WeightResult) for r in results)


# --- CLI ---

def test_cmd_check_prints_expression():
    out = captured(cmd_weight_check, expression="0 9 * * *")
    assert "0 9 * * *" in out


def test_cmd_check_prints_grade():
    out = captured(cmd_weight_check, expression="0 9 * * *")
    assert "grade" in out.lower() or any(g in out for g in ("featherlight", "light", "moderate", "heavy", "crushing"))


def test_cmd_score_prints_float():
    out = captured(cmd_weight_score, expression="* * * * *")
    assert float(out.strip()) >= 0.9


def test_cmd_grade_prints_label():
    out = captured(cmd_weight_grade, expression="0 0 * * 0")
    assert out.strip() in ("featherlight", "light", "moderate", "heavy", "crushing")


def test_cmd_json_is_valid_json():
    out = captured(cmd_weight_json, expression="0 9 * * *")
    data = json.loads(out)
    assert "score" in data
    assert "grade" in data
    assert "runs_per_day" in data


def test_cmd_batch_prints_all_expressions():
    out = captured(cmd_weight_batch, expressions=["* * * * *", "0 9 * * *"])
    assert "* * * * *" in out
    assert "0 9 * * *" in out
