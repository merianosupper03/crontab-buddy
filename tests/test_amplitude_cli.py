"""Tests for crontab_buddy.amplitude_cli."""

import io
import sys
import pytest
from crontab_buddy.amplitude_cli import (
    cmd_amplitude_check,
    cmd_amplitude_score,
    cmd_amplitude_grade,
    cmd_amplitude_batch,
    cmd_amplitude_json,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def captured(capsys):
    yield capsys


def test_cmd_check_prints_expression(captured):
    cmd_amplitude_check(Args(expression="* * * * *"))
    out = captured.readouterr().out
    assert "* * * * *" in out


def test_cmd_check_prints_grade(captured):
    cmd_amplitude_check(Args(expression="* * * * *"))
    out = captured.readouterr().out
    assert "maximal" in out


def test_cmd_check_prints_score(captured):
    cmd_amplitude_check(Args(expression="* * * * *"))
    out = captured.readouterr().out
    assert "Score" in out


def test_cmd_check_invalid_prints_error(captured):
    cmd_amplitude_check(Args(expression="bad expr"))
    out = captured.readouterr().out
    assert "Error" in out or "error" in out


def test_cmd_score_prints_float(captured):
    cmd_amplitude_score(Args(expression="* * * * *"))
    out = captured.readouterr().out.strip()
    assert float(out) == pytest.approx(1.0, abs=0.01)


def test_cmd_score_invalid_prints_error(captured):
    cmd_amplitude_score(Args(expression="bad"))
    out = captured.readouterr().out
    assert "error" in out


def test_cmd_grade_prints_grade(captured):
    cmd_amplitude_grade(Args(expression="* * * * *"))
    out = captured.readouterr().out.strip()
    assert out == "maximal"


def test_cmd_grade_invalid_prints_error(captured):
    cmd_amplitude_grade(Args(expression="bad"))
    out = captured.readouterr().out
    assert "error" in out


def test_cmd_batch_prints_rows(captured):
    cmd_amplitude_batch(Args(expressions=["* * * * *", "0 0 * * *"]))
    out = captured.readouterr().out
    assert "* * * * *" in out
    assert "0 0 * * *" in out


def test_cmd_batch_skips_empty(captured):
    cmd_amplitude_batch(Args(expressions=["  ", "* * * * *"]))
    out = captured.readouterr().out
    assert "* * * * *" in out


def test_cmd_json_prints_json(captured):
    import json
    cmd_amplitude_json(Args(expression="* * * * *"))
    out = captured.readouterr().out
    data = json.loads(out)
    assert "score" in data
    assert "grade" in data
    assert "scores" in data


def test_cmd_json_invalid_has_error_key(captured):
    import json
    cmd_amplitude_json(Args(expression="bad"))
    out = captured.readouterr().out
    data = json.loads(out)
    assert data["error"] is not None
