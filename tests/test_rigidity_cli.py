"""Tests for crontab_buddy.rigidity_cli."""

import pytest
from crontab_buddy.rigidity_cli import (
    cmd_rigidity_check,
    cmd_rigidity_score,
    cmd_rigidity_grade,
    cmd_rigidity_batch,
    cmd_rigidity_json,
)


class Args:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def captured(cmd, **kwargs):
    lines = []
    cmd(Args(**kwargs), print_fn=lines.append)
    return lines


def test_cmd_check_prints_expression():
    lines = captured(cmd_rigidity_check, expression="0 9 * * 1")
    assert any("0 9 * * 1" in l for l in lines)


def test_cmd_check_prints_grade():
    lines = captured(cmd_rigidity_check, expression="0 9 * * 1")
    assert any("Grade" in l for l in lines)


def test_cmd_check_prints_score():
    lines = captured(cmd_rigidity_check, expression="0 9 * * 1")
    assert any("Score" in l for l in lines)


def test_cmd_check_invalid_expression_prints_error():
    lines = captured(cmd_rigidity_check, expression="not valid")
    assert any("Error" in l for l in lines)


def test_cmd_score_prints_float():
    lines = captured(cmd_rigidity_score, expression="30 9 15 6 2")
    assert len(lines) == 1
    val = float(lines[0])
    assert 0.0 <= val <= 1.0


def test_cmd_score_invalid_prints_error():
    lines = captured(cmd_rigidity_score, expression="bad")
    assert any("Error" in l for l in lines)


def test_cmd_grade_prints_grade_string():
    lines = captured(cmd_rigidity_grade, expression="* * * * *")
    assert lines[0] == "supple"


def test_cmd_grade_invalid_prints_error():
    lines = captured(cmd_rigidity_grade, expression="nope")
    assert any("Error" in l for l in lines)


def test_cmd_batch_prints_one_line_per_expression():
    lines = captured(
        cmd_rigidity_batch,
        expressions=["* * * * *", "0 9 * * 1"]
    )
    assert len(lines) == 2


def test_cmd_batch_handles_invalid_expression():
    lines = captured(cmd_rigidity_batch, expressions=["bad expr"])
    assert any("ERROR" in l for l in lines)


def test_cmd_json_outputs_valid_json():
    import json
    lines = captured(cmd_rigidity_json, expression="0 9 * * 1")
    data = json.loads("\n".join(lines))
    assert "expression" in data
    assert "score" in data
    assert "grade" in data
    assert "scores" in data


def test_cmd_json_invalid_expression_has_error_key():
    import json
    lines = captured(cmd_rigidity_json, expression="bad")
    data = json.loads("\n".join(lines))
    assert data["error"] != ""
