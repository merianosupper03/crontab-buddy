"""Tests for crontab_buddy.flow_cli."""

import io
import sys
import pytest
from crontab_buddy.flow_cli import (
    cmd_flow_check,
    cmd_flow_score,
    cmd_flow_grade,
    cmd_flow_batch,
    cmd_flow_json,
)


class Args:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def captured(fn, args):
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        fn(args)
    finally:
        sys.stdout = old
    return buf.getvalue()


def test_cmd_check_prints_expression():
    out = captured(cmd_flow_check, Args(expression="* * * * *"))
    assert "* * * * *" in out


def test_cmd_check_prints_grade():
    out = captured(cmd_flow_check, Args(expression="* * * * *"))
    assert "Grade" in out


def test_cmd_check_prints_score():
    out = captured(cmd_flow_check, Args(expression="* * * * *"))
    assert "Score" in out


def test_cmd_check_invalid_expression_prints_error():
    out = captured(cmd_flow_check, Args(expression="bad bad bad"))
    assert "Error" in out or "error" in out


def test_cmd_score_prints_float():
    out = captured(cmd_flow_score, Args(expression="0 * * * *"))
    val = float(out.strip())
    assert 0.0 <= val <= 1.0


def test_cmd_score_invalid_prints_error():
    out = captured(cmd_flow_score, Args(expression="99 99 99 99 99"))
    assert "error" in out.lower()


def test_cmd_grade_prints_label():
    out = captured(cmd_flow_grade, Args(expression="* * * * *"))
    assert out.strip() in ("fluid", "smooth", "uneven", "choppy", "erratic")


def test_cmd_batch_prints_multiple_lines():
    out = captured(
        cmd_flow_batch,
        Args(expressions=["* * * * *", "0 * * * *", "0 9 * * *"]),
    )
    lines = [l for l in out.strip().splitlines() if l]
    assert len(lines) == 3


def test_cmd_batch_invalid_shows_error():
    out = captured(cmd_flow_batch, Args(expressions=["not valid"]))
    assert "error" in out.lower()


def test_cmd_json_is_valid_json():
    import json
    out = captured(cmd_flow_json, Args(expression="*/10 * * * *"))
    data = json.loads(out)
    assert "score" in data
    assert "grade" in data
    assert "transitions" in data


def test_cmd_json_invalid_expression_has_error_key():
    import json
    out = captured(cmd_flow_json, Args(expression="bad"))
    data = json.loads(out)
    assert data["error"] is not None
