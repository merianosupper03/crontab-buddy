"""Tests for crontab_buddy.resolution_cli."""

import io
import sys
import pytest
from crontab_buddy.resolution_cli import (
    cmd_resolution_check,
    cmd_resolution_score,
    cmd_resolution_grade,
    cmd_resolution_batch,
    cmd_resolution_json,
)


class Args:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def captured(func, args):
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        func(args)
    finally:
        sys.stdout = old
    return buf.getvalue()


def test_cmd_check_prints_expression():
    out = captured(cmd_resolution_check, Args(expression="* * * * *"))
    assert "* * * * *" in out


def test_cmd_check_prints_grade():
    out = captured(cmd_resolution_check, Args(expression="* * * * *"))
    assert "Grade" in out


def test_cmd_check_prints_score():
    out = captured(cmd_resolution_check, Args(expression="* * * * *"))
    assert "Score" in out


def test_cmd_check_invalid_expression_prints_error():
    out = captured(cmd_resolution_check, Args(expression="not valid at all"))
    assert "Error" in out or "error" in out


def test_cmd_score_prints_float():
    out = captured(cmd_resolution_score, Args(expression="*/5 * * * *"))
    val = float(out.strip())
    assert 0.0 <= val <= 1.0


def test_cmd_score_invalid_prints_error():
    out = captured(cmd_resolution_score, Args(expression="bad"))
    assert "error" in out.lower()


def test_cmd_grade_prints_label():
    out = captured(cmd_resolution_grade, Args(expression="* * * * *"))
    assert out.strip() in ("atomic", "fine", "moderate", "coarse", "blunt")


def test_cmd_grade_invalid_prints_error():
    out = captured(cmd_resolution_grade, Args(expression="bad"))
    assert "error" in out.lower()


def test_cmd_batch_prints_all_expressions():
    out = captured(
        cmd_resolution_batch,
        Args(expressions=["* * * * *", "0 9 * * 1"]),
    )
    assert "* * * * *" in out
    assert "0 9 * * 1" in out


def test_cmd_batch_handles_invalid():
    out = captured(cmd_resolution_batch, Args(expressions=["bad expr"]))
    assert "error" in out.lower()


def test_cmd_json_outputs_valid_json():
    import json
    out = captured(cmd_resolution_json, Args(expression="*/15 * * * *"))
    data = json.loads(out)
    assert "score" in data
    assert "grade" in data
    assert "scores" in data


def test_cmd_json_invalid_has_error_key():
    import json
    out = captured(cmd_resolution_json, Args(expression="bad"))
    data = json.loads(out)
    assert data["error"] is not None
