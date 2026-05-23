"""Tests for crontab_buddy.friction_score_cli."""

import io
import sys
import pytest
from crontab_buddy.friction_score_cli import (
    cmd_friction_score_check,
    cmd_friction_score_grade,
    cmd_friction_score_value,
    cmd_friction_score_batch,
    cmd_friction_score_json,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class captured:
    def __init__(self):
        self._buf = io.StringIO()
        self._old = None

    def __enter__(self):
        self._old = sys.stdout
        sys.stdout = self._buf
        return self._buf

    def __exit__(self, *_):
        sys.stdout = self._old


def test_cmd_check_prints_expression():
    args = Args(expression="0 9 * * *")
    with captured() as out:
        cmd_friction_score_check(args)
    assert "0 9 * * *" in out.getvalue()


def test_cmd_check_prints_score():
    args = Args(expression="0 9 * * *")
    with captured() as out:
        cmd_friction_score_check(args)
    assert "Score" in out.getvalue()


def test_cmd_check_prints_grade():
    args = Args(expression="* * * * *")
    with captured() as out:
        cmd_friction_score_check(args)
    assert "Grade" in out.getvalue()


def test_cmd_check_invalid_expression_prints_error():
    args = Args(expression="not valid at all")
    with captured() as out:
        cmd_friction_score_check(args)
    assert "Error" in out.getvalue()


def test_cmd_grade_prints_grade_string():
    args = Args(expression="* * * * *")
    with captured() as out:
        cmd_friction_score_grade(args)
    assert out.getvalue().strip() in (
        "smooth", "manageable", "moderate", "dense", "impenetrable"
    )


def test_cmd_value_prints_float():
    args = Args(expression="0 0 * * *")
    with captured() as out:
        cmd_friction_score_value(args)
    val = out.getvalue().strip()
    assert float(val) >= 0.0


def test_cmd_batch_prints_each_expression():
    args = Args(expressions="* * * * *,0 9 * * 1")
    with captured() as out:
        cmd_friction_score_batch(args)
    text = out.getvalue()
    assert "* * * * *" in text
    assert "0 9 * * 1" in text


def test_cmd_batch_invalid_shows_error():
    args = Args(expressions="bad_expr,* * * * *")
    with captured() as out:
        cmd_friction_score_batch(args)
    assert "error" in out.getvalue().lower()


def test_cmd_json_outputs_valid_json():
    import json
    args = Args(expression="*/5 * * * *")
    with captured() as out:
        cmd_friction_score_json(args)
    data = json.loads(out.getvalue())
    assert "expression" in data
    assert "score" in data
    assert "grade" in data
    assert "scores" in data


def test_cmd_json_invalid_includes_error_key():
    import json
    args = Args(expression="totally wrong")
    with captured() as out:
        cmd_friction_score_json(args)
    data = json.loads(out.getvalue())
    assert "error" in data
