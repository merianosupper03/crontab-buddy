"""Tests for crontab_buddy.sparsity_cli."""

import io
import sys
import pytest

from crontab_buddy.sparsity_cli import (
    cmd_sparsity_check,
    cmd_sparsity_score,
    cmd_sparsity_grade,
    cmd_sparsity_batch,
    cmd_sparsity_json,
)


class Args:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@pytest.fixture
def captured(capsys):
    yield capsys


def test_cmd_check_prints_expression(captured):
    cmd_sparsity_check(Args(expression="0 0 * * *"))
    out = captured.readouterr().out
    assert "0 0 * * *" in out


def test_cmd_check_prints_grade(captured):
    cmd_sparsity_check(Args(expression="0 0 * * *"))
    out = captured.readouterr().out
    assert "Grade" in out


def test_cmd_check_prints_score(captured):
    cmd_sparsity_check(Args(expression="0 0 * * *"))
    out = captured.readouterr().out
    assert "Score" in out


def test_cmd_check_invalid_expression_prints_error(captured):
    cmd_sparsity_check(Args(expression="not valid"))
    out = captured.readouterr().out
    assert "Error" in out


def test_cmd_score_prints_float(captured):
    cmd_sparsity_score(Args(expression="0 0 * * *"))
    out = captured.readouterr().out.strip()
    assert float(out) >= 0.0


def test_cmd_score_invalid_prints_error(captured):
    cmd_sparsity_score(Args(expression="bad"))
    out = captured.readouterr().out
    assert "Error" in out


def test_cmd_grade_prints_label(captured):
    cmd_sparsity_grade(Args(expression="0 9 * * 1"))
    out = captured.readouterr().out.strip()
    assert out in ("glacial", "sparse", "infrequent", "occasional", "moderate", "dense", "saturated")


def test_cmd_grade_invalid_prints_error(captured):
    cmd_sparsity_grade(Args(expression="x x x x x"))
    out = captured.readouterr().out
    assert "Error" in out


def test_cmd_batch_prints_all(captured):
    cmd_sparsity_batch(Args(expressions=["* * * * *", "0 0 * * *"]))
    out = captured.readouterr().out
    assert "* * * * *" in out
    assert "0 0 * * *" in out


def test_cmd_json_output_is_valid(captured):
    import json
    cmd_sparsity_json(Args(expression="0 0 * * *"))
    out = captured.readouterr().out
    data = json.loads(out)
    assert "grade" in data
    assert "score" in data
    assert "interval_seconds" in data


def test_cmd_json_invalid_expression(captured):
    import json
    cmd_sparsity_json(Args(expression="bad expr"))
    out = captured.readouterr().out
    data = json.loads(out)
    assert data["error"] is not None
