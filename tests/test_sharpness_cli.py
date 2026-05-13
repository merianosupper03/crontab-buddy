"""Tests for crontab_buddy.sharpness_cli."""

import io
import sys
import pytest
from crontab_buddy.sharpness_cli import (
    cmd_sharpness_check,
    cmd_sharpness_score,
    cmd_sharpness_grade,
    cmd_sharpness_batch,
    cmd_sharpness_json,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def captured(capsys):
    yield capsys


def test_cmd_check_prints_expression(captured):
    cmd_sharpness_check(Args(expression="0 12 * * *"))
    out = captured.readouterr().out
    assert "0 12 * * *" in out


def test_cmd_check_prints_grade(captured):
    cmd_sharpness_check(Args(expression="0 12 * * *"))
    out = captured.readouterr().out
    assert "Grade" in out


def test_cmd_check_prints_field_scores(captured):
    cmd_sharpness_check(Args(expression="30 6 1 1 1"))
    out = captured.readouterr().out
    assert "minute" in out
    assert "hour" in out


def test_cmd_check_invalid_expression(captured):
    cmd_sharpness_check(Args(expression="not valid"))
    out = captured.readouterr().out
    assert "Error" in out


def test_cmd_score_prints_float(captured):
    cmd_sharpness_score(Args(expression="0 0 * * *"))
    out = captured.readouterr().out.strip()
    assert float(out) >= 0.0


def test_cmd_score_invalid_prints_error(captured):
    cmd_sharpness_score(Args(expression="bad"))
    out = captured.readouterr().out
    assert "Error" in out


def test_cmd_grade_prints_label(captured):
    cmd_sharpness_grade(Args(expression="* * * * *"))
    out = captured.readouterr().out.strip()
    assert out == "dull"


def test_cmd_grade_invalid_prints_error(captured):
    cmd_sharpness_grade(Args(expression="bad"))
    out = captured.readouterr().out
    assert "Error" in out


def test_cmd_batch_prints_all_expressions(captured):
    exprs = ["* * * * *", "0 12 * * *", "bad"]
    cmd_sharpness_batch(Args(expressions=exprs))
    out = captured.readouterr().out
    assert "* * * * *" in out
    assert "0 12 * * *" in out
    assert "ERROR" in out


def test_cmd_json_contains_keys(captured):
    import json
    cmd_sharpness_json(Args(expression="0 6 * * 1"))
    out = captured.readouterr().out
    data = json.loads(out)
    assert "expression" in data
    assert "score" in data
    assert "grade" in data
    assert "scores" in data


def test_cmd_json_invalid_expression(captured):
    import json
    cmd_sharpness_json(Args(expression="nope"))
    out = captured.readouterr().out
    data = json.loads(out)
    assert data["error"] is not None
