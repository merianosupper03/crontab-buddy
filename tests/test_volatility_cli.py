"""Tests for crontab_buddy.volatility_cli."""

import io
import sys
import pytest
from crontab_buddy.volatility_cli import (
    cmd_volatility_check,
    cmd_volatility_level,
    cmd_volatility_score,
    cmd_volatility_batch,
    cmd_volatility_json,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def captured(capsys):
    return capsys


def test_cmd_check_prints_level(captured):
    cmd_volatility_check(Args(expression="* * * * *"))
    out = captured.readouterr().out
    assert "Level" in out
    assert "extreme" in out


def test_cmd_check_prints_score(captured):
    cmd_volatility_check(Args(expression="* * * * *"))
    out = captured.readouterr().out
    assert "Score" in out


def test_cmd_check_invalid_prints_error(captured):
    cmd_volatility_check(Args(expression="not valid"))
    out = captured.readouterr().out
    assert "error" in out.lower()


def test_cmd_level_prints_level_only(captured):
    cmd_volatility_level(Args(expression="* * * * *"))
    out = captured.readouterr().out.strip()
    assert out in ("extreme", "very_high", "high", "moderate", "low", "very_low", "stable")


def test_cmd_level_invalid_prints_error(captured):
    cmd_volatility_level(Args(expression="bad"))
    out = captured.readouterr().out
    assert "error" in out.lower()


def test_cmd_score_prints_float(captured):
    cmd_volatility_score(Args(expression="* * * * *"))
    out = captured.readouterr().out.strip()
    assert float(out) >= 0.0


def test_cmd_score_invalid_prints_error(captured):
    cmd_volatility_score(Args(expression="bad expr"))
    out = captured.readouterr().out
    assert "error" in out.lower()


def test_cmd_batch_prints_multiple(captured):
    cmd_volatility_batch(Args(expressions=["* * * * *", "0 9 * * *"]))
    out = captured.readouterr().out
    assert "* * * * *" in out
    assert "0 9 * * *" in out


def test_cmd_batch_skips_empty(captured):
    cmd_volatility_batch(Args(expressions=["  ", "* * * * *"]))
    out = captured.readouterr().out
    lines = [l for l in out.strip().splitlines() if l.strip()]
    assert len(lines) == 1


def test_cmd_json_outputs_valid_json(captured):
    import json
    cmd_volatility_json(Args(expression="* * * * *"))
    out = captured.readouterr().out
    data = json.loads(out)
    assert "level" in data
    assert "score" in data
    assert data["valid"] is True
