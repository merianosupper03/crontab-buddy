"""Tests for crontab_buddy.isolation_cli."""
import json
import pytest
from crontab_buddy.isolation_cli import (
    cmd_isolation_check,
    cmd_isolation_score,
    cmd_isolation_grade,
    cmd_isolation_batch,
    cmd_isolation_json,
)


class Args:
    def __init__(self, expression="0 9 * * *", peers=None, expressions=None):
        self.expression = expression
        self.peers = peers or []
        self.expressions = expressions or []


@pytest.fixture
def captured():
    lines = []
    return lines, lines.append


def test_cmd_check_prints_expression(captured):
    lines, out = captured
    cmd_isolation_check(Args("0 9 * * *"), out=out)
    combined = "\n".join(lines)
    assert "0 9 * * *" in combined


def test_cmd_check_prints_score(captured):
    lines, out = captured
    cmd_isolation_check(Args("0 9 * * *"), out=out)
    combined = "\n".join(lines)
    assert "Score" in combined


def test_cmd_check_invalid_expression_prints_error(captured):
    lines, out = captured
    cmd_isolation_check(Args("not valid"), out=out)
    combined = "\n".join(lines)
    assert "Error" in combined


def test_cmd_score_prints_float(captured):
    lines, out = captured
    cmd_isolation_score(Args("0 9 * * *"), out=out)
    assert len(lines) == 1
    float(lines[0])  # should not raise


def test_cmd_grade_prints_label(captured):
    lines, out = captured
    cmd_isolation_grade(Args("0 9 * * *"), out=out)
    assert lines[0] in {"isolated", "sparse", "moderate", "crowded"}


def test_cmd_batch_prints_each_expression(captured):
    lines, out = captured
    cmd_isolation_batch(Args(expressions=["0 9 * * *", "0 22 * * *"]), out=out)
    assert len(lines) == 2
    assert "0 9 * * *" in lines[0]
    assert "0 22 * * *" in lines[1]


def test_cmd_batch_invalid_expression_shows_error(captured):
    lines, out = captured
    cmd_isolation_batch(Args(expressions=["bad", "0 9 * * *"]), out=out)
    assert "ERROR" in lines[0]


def test_cmd_json_is_valid_json(captured):
    lines, out = captured
    cmd_isolation_json(Args("0 9 * * *"), out=out)
    data = json.loads(lines[0])
    assert "expression" in data
    assert "score" in data
    assert "grade" in data
    assert "neighbours" in data


def test_cmd_json_error_field_none_for_valid(captured):
    lines, out = captured
    cmd_isolation_json(Args("0 9 * * *"), out=out)
    data = json.loads(lines[0])
    assert data["error"] is None
