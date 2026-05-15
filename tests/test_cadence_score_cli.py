"""Tests for crontab_buddy.cadence_score_cli."""

import io
import sys
import pytest

from crontab_buddy.cadence_score_cli import (
    cmd_cadence_score_check,
    cmd_cadence_score_grade,
    cmd_cadence_score_value,
    cmd_cadence_score_batch,
    cmd_cadence_score_json,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def captured(fn, *args, **kwargs):
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        fn(*args, **kwargs)
    finally:
        sys.stdout = old
    return buf.getvalue()


def test_cmd_check_prints_expression():
    out = captured(cmd_cadence_score_check, Args(expression="0 9 * * 1"))
    assert "0 9 * * 1" in out


def test_cmd_check_prints_score():
    out = captured(cmd_cadence_score_check, Args(expression="0 9 * * 1"))
    assert "Score" in out


def test_cmd_check_prints_grade():
    out = captured(cmd_cadence_score_check, Args(expression="0 9 * * 1"))
    assert "Grade" in out


def test_cmd_check_invalid_expression_prints_error():
    out = captured(cmd_cadence_score_check, Args(expression="not valid"))
    assert "Error" in out


def test_cmd_grade_prints_letter():
    out = captured(cmd_cadence_score_grade, Args(expression="0 9 * * 1"))
    assert out.strip() in {"A", "B", "C", "D", "F"}


def test_cmd_value_prints_float():
    out = captured(cmd_cadence_score_value, Args(expression="0 9 * * 1"))
    val = float(out.strip())
    assert 0.0 <= val <= 1.0


def test_cmd_batch_prints_all_expressions():
    args = Args(expressions=["* * * * *", "0 9 * * 1"])
    out = captured(cmd_cadence_score_batch, args)
    assert "* * * * *" in out
    assert "0 9 * * 1" in out


def test_cmd_batch_invalid_shows_error():
    args = Args(expressions=["bad expr"])
    out = captured(cmd_cadence_score_batch, args)
    assert "ERROR" in out


def test_cmd_json_is_valid_json():
    import json
    out = captured(cmd_cadence_score_json, Args(expression="0 9 * * 1"))
    data = json.loads(out)
    assert "score" in data
    assert "grade" in data


def test_cmd_json_invalid_expression_has_error_key():
    import json
    out = captured(cmd_cadence_score_json, Args(expression="bad"))
    data = json.loads(out)
    assert data["error"] is not None
