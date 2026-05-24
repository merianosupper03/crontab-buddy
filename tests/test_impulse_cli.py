"""Tests for crontab_buddy.impulse_cli."""

import io
import sys
import pytest
from crontab_buddy.impulse_cli import (
    cmd_impulse_check, cmd_impulse_score, cmd_impulse_grade,
    cmd_impulse_batch, cmd_impulse_json,
)


class Args:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class captured:
    def __init__(self):
        self._buf = io.StringIO()

    def __enter__(self):
        self._old = sys.stdout
        sys.stdout = self._buf
        return self._buf

    def __exit__(self, *_):
        sys.stdout = self._old


def test_cmd_check_prints_expression():
    args = Args(expression="* * * * *")
    with captured() as buf:
        cmd_impulse_check(args)
    assert "* * * * *" in buf.getvalue()


def test_cmd_check_prints_grade():
    args = Args(expression="* * * * *")
    with captured() as buf:
        cmd_impulse_check(args)
    assert "flat" in buf.getvalue()


def test_cmd_check_invalid_prints_error():
    args = Args(expression="not valid")
    with captured() as buf:
        cmd_impulse_check(args)
    assert "Error" in buf.getvalue()


def test_cmd_score_prints_float():
    args = Args(expression="0 12 * * *")
    with captured() as buf:
        cmd_impulse_score(args)
    out = buf.getvalue().strip()
    assert float(out) == 1.0


def test_cmd_score_invalid_prints_error():
    args = Args(expression="bad")
    with captured() as buf:
        cmd_impulse_score(args)
    assert "error" in buf.getvalue()


def test_cmd_grade_prints_label():
    args = Args(expression="0 12 * * *")
    with captured() as buf:
        cmd_impulse_grade(args)
    assert "explosive" in buf.getvalue()


def test_cmd_batch_prints_multiple():
    args = Args(expressions=["* * * * *", "0 12 * * *"])
    with captured() as buf:
        cmd_impulse_batch(args)
    out = buf.getvalue()
    assert "flat" in out
    assert "explosive" in out


def test_cmd_json_output():
    import json
    args = Args(expression="0 6 * * *")
    with captured() as buf:
        cmd_impulse_json(args)
    data = json.loads(buf.getvalue())
    assert "score" in data
    assert "grade" in data
    assert data["expression"] == "0 6 * * *"


def test_cmd_json_invalid():
    import json
    args = Args(expression="bad expr")
    with captured() as buf:
        cmd_impulse_json(args)
    data = json.loads(buf.getvalue())
    assert data["error"] is not None
