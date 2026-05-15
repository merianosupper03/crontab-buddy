"""Tests for crontab_buddy.inertia_cli."""

import json
import pytest
from crontab_buddy.inertia_cli import (
    cmd_inertia_check,
    cmd_inertia_score,
    cmd_inertia_grade,
    cmd_inertia_batch,
    cmd_inertia_json,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def captured(cmd, **kwargs):
    lines = []
    cmd(Args(**kwargs), print_fn=lines.append)
    return lines


def test_cmd_check_prints_expression():
    lines = captured(cmd_inertia_check, expression="* * * * *")
    combined = "\n".join(lines)
    assert "* * * * *" in combined


def test_cmd_check_prints_score():
    lines = captured(cmd_inertia_check, expression="0 9 * * *")
    combined = "\n".join(lines)
    assert "Score" in combined


def test_cmd_check_prints_grade():
    lines = captured(cmd_inertia_check, expression="0 9 * * *")
    combined = "\n".join(lines)
    assert "Grade" in combined


def test_cmd_check_invalid_prints_error():
    lines = captured(cmd_inertia_check, expression="not valid")
    combined = "\n".join(lines)
    assert "Error" in combined


def test_cmd_score_prints_float():
    lines = captured(cmd_inertia_score, expression="0 * * * *")
    assert len(lines) == 1
    val = float(lines[0])
    assert 0.0 <= val <= 1.0


def test_cmd_score_invalid_prints_error():
    lines = captured(cmd_inertia_score, expression="bad expr")
    combined = "\n".join(lines)
    assert "Error" in combined


def test_cmd_grade_prints_label():
    lines = captured(cmd_inertia_grade, expression="0 9 * * 1")
    assert len(lines) == 1
    assert lines[0] in ("fluid", "flexible", "moderate", "resistant", "immovable")


def test_cmd_grade_invalid_prints_error():
    lines = captured(cmd_inertia_grade, expression="x y z")
    combined = "\n".join(lines)
    assert "Error" in combined


def test_cmd_batch_prints_all_expressions():
    exprs = ["* * * * *", "0 9 * * *"]
    lines = captured(cmd_inertia_batch, expressions=exprs)
    assert len(lines) == 2


def test_cmd_batch_shows_grade():
    lines = captured(cmd_inertia_batch, expressions=["0 9 * * *"])
    assert "grade=" in lines[0]


def test_cmd_json_is_valid_json():
    lines = captured(cmd_inertia_json, expression="0 9 * * *")
    data = json.loads("\n".join(lines))
    assert "expression" in data
    assert "score" in data
    assert "grade" in data


def test_cmd_json_invalid_expression_has_error_key():
    lines = captured(cmd_inertia_json, expression="bad")
    data = json.loads("\n".join(lines))
    assert data["error"] is not None
