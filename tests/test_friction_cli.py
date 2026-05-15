import json
import pytest
from io import StringIO
from unittest.mock import patch
from crontab_buddy.friction_cli import (
    cmd_friction_check,
    cmd_friction_score,
    cmd_friction_grade,
    cmd_friction_batch,
    cmd_friction_json,
)


class Args:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@pytest.fixture
def captured(capsys):
    return capsys


def test_cmd_check_prints_expression(captured):
    cmd_friction_check(Args(expression="0 9 * * 1"))
    out = captured.readouterr().out
    assert "0 9 * * 1" in out


def test_cmd_check_prints_grade(captured):
    cmd_friction_check(Args(expression="0 9 * * 1"))
    out = captured.readouterr().out
    assert "Grade" in out


def test_cmd_check_prints_score(captured):
    cmd_friction_check(Args(expression="0 9 * * 1"))
    out = captured.readouterr().out
    assert "Score" in out


def test_cmd_check_invalid_expression(captured):
    cmd_friction_check(Args(expression="bad expr"))
    out = captured.readouterr().out
    assert "Error" in out or "error" in out


def test_cmd_score_prints_float(captured):
    cmd_friction_score(Args(expression="* * * * *"))
    out = captured.readouterr().out.strip()
    assert float(out) == 0.0


def test_cmd_score_invalid_prints_error(captured):
    cmd_friction_score(Args(expression="nope"))
    out = captured.readouterr().out
    assert "error" in out


def test_cmd_grade_prints_grade(captured):
    cmd_friction_grade(Args(expression="* * * * *"))
    out = captured.readouterr().out.strip()
    assert out == "frictionless"


def test_cmd_grade_invalid_prints_error(captured):
    cmd_friction_grade(Args(expression="???"))
    out = captured.readouterr().out
    assert "error" in out


def test_cmd_batch_prints_all(captured):
    cmd_friction_batch(Args(expressions=["* * * * *", "0 9 * * 1"]))
    out = captured.readouterr().out
    assert "* * * * *" in out
    assert "0 9 * * 1" in out


def test_cmd_batch_invalid_shows_error(captured):
    cmd_friction_batch(Args(expressions=["bad"]))
    out = captured.readouterr().out
    assert "error" in out


def test_cmd_json_valid(captured):
    cmd_friction_json(Args(expression="0 9 * * 1"))
    out = captured.readouterr().out
    data = json.loads(out)
    assert "score" in data
    assert "grade" in data
    assert "scores" in data


def test_cmd_json_invalid(captured):
    cmd_friction_json(Args(expression="bad"))
    out = captured.readouterr().out
    data = json.loads(out)
    assert data["error"] is not None
