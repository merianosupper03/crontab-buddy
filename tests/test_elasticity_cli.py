"""Tests for crontab_buddy.elasticity_cli."""

import io
import sys
import pytest
from crontab_buddy.elasticity_cli import (
    cmd_elasticity_check,
    cmd_elasticity_score,
    cmd_elasticity_grade,
    cmd_elasticity_batch,
    cmd_elasticity_json,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


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
    out = captured(cmd_elasticity_check, Args(expression="* * * * *"))
    assert "* * * * *" in out


def test_cmd_check_prints_grade():
    out = captured(cmd_elasticity_check, Args(expression="* * * * *"))
    assert "supple" in out


def test_cmd_check_prints_score():
    out = captured(cmd_elasticity_check, Args(expression="* * * * *"))
    assert "1.000" in out


def test_cmd_check_invalid_expression_prints_error():
    out = captured(cmd_elasticity_check, Args(expression="bad expr"))
    assert "Error" in out or "error" in out


def test_cmd_score_prints_float():
    out = captured(cmd_elasticity_score, Args(expression="* * * * *"))
    assert float(out.strip()) == pytest.approx(1.0)


def test_cmd_score_invalid_prints_error():
    out = captured(cmd_elasticity_score, Args(expression="bad"))
    assert "error" in out.lower()


def test_cmd_grade_prints_grade():
    out = captured(cmd_elasticity_grade, Args(expression="* * * * *"))
    assert out.strip() == "supple"


def test_cmd_grade_invalid_prints_error():
    out = captured(cmd_elasticity_grade, Args(expression="bad"))
    assert "error" in out.lower()


def test_cmd_batch_prints_multiple():
    args = Args(expressions=["* * * * *", "0 9 * * *"])
    out = captured(cmd_elasticity_batch, args)
    assert "* * * * *" in out
    assert "0 9 * * *" in out


def test_cmd_batch_marks_errors():
    args = Args(expressions=["bad expr"])
    out = captured(cmd_elasticity_batch, args)
    assert "ERROR" in out


def test_cmd_json_has_score_key():
    import json
    out = captured(cmd_elasticity_json, Args(expression="* * * * *"))
    data = json.loads(out)
    assert "score" in data
    assert "grade" in data
    assert data["score"] == pytest.approx(1.0)


def test_cmd_json_invalid_has_error_key():
    import json
    out = captured(cmd_elasticity_json, Args(expression="bad"))
    data = json.loads(out)
    assert data["error"] is not None
