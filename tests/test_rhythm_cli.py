"""Tests for crontab_buddy.rhythm_cli."""

import json
import io
from contextlib import redirect_stdout

import pytest

from crontab_buddy.rhythm_cli import (
    cmd_rhythm_check,
    cmd_rhythm_score,
    cmd_rhythm_level,
    cmd_rhythm_batch,
    cmd_rhythm_json,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def captured(fn, *args, **kwargs):
    buf = io.StringIO()
    with redirect_stdout(buf):
        fn(*args, **kwargs)
    return buf.getvalue()


def test_cmd_check_prints_expression():
    out = captured(cmd_rhythm_check, Args(expression="* * * * *"))
    assert "* * * * *" in out


def test_cmd_check_prints_level():
    out = captured(cmd_rhythm_check, Args(expression="* * * * *"))
    assert "metronomic" in out


def test_cmd_check_prints_score():
    out = captured(cmd_rhythm_check, Args(expression="* * * * *"))
    assert "Score" in out


def test_cmd_check_invalid_expression_prints_error():
    out = captured(cmd_rhythm_check, Args(expression="not valid"))
    assert "Error" in out or "error" in out


def test_cmd_score_prints_float():
    out = captured(cmd_rhythm_score, Args(expression="* * * * *"))
    val = float(out.strip())
    assert 0.0 <= val <= 1.0


def test_cmd_score_invalid_prints_error():
    out = captured(cmd_rhythm_score, Args(expression="bad"))
    assert "error" in out.lower()


def test_cmd_level_prints_string():
    out = captured(cmd_rhythm_level, Args(expression="*/15 * * * *"))
    assert out.strip() in ("metronomic", "steady", "irregular", "erratic", "chaotic")


def test_cmd_batch_prints_multiple_lines():
    out = captured(
        cmd_rhythm_batch,
        Args(expressions=["* * * * *", "0 6 * * *"]),
    )
    lines = [l for l in out.strip().splitlines() if l]
    assert len(lines) == 2


def test_cmd_json_is_valid_json():
    out = captured(cmd_rhythm_json, Args(expression="*/30 * * * *"))
    data = json.loads(out)
    assert "expression" in data
    assert "score" in data
    assert "level" in data
    assert "intervals" in data


def test_cmd_json_invalid_expression_has_error_key():
    out = captured(cmd_rhythm_json, Args(expression="bad expr"))
    data = json.loads(out)
    assert data["error"] is not None
