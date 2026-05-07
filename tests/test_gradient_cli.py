"""Tests for crontab_buddy.gradient_cli"""

import json
import pytest
from crontab_buddy.gradient_cli import (
    cmd_gradient_check,
    cmd_gradient_score,
    cmd_gradient_label,
    cmd_gradient_batch,
    cmd_gradient_json,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def captured():
    lines = []
    return lines, lines.append


def test_cmd_check_prints_expression(captured):
    lines, fn = captured
    cmd_gradient_check(Args(expression="*/5 * * * *"), print_fn=fn)
    combined = "\n".join(lines)
    assert "*/5 * * * *" in combined


def test_cmd_check_prints_gradient_label(captured):
    lines, fn = captured
    cmd_gradient_check(Args(expression="* * * * *"), print_fn=fn)
    combined = "\n".join(lines)
    assert "smooth" in combined


def test_cmd_check_prints_score(captured):
    lines, fn = captured
    cmd_gradient_check(Args(expression="* * * * *"), print_fn=fn)
    combined = "\n".join(lines)
    assert "Score" in combined


def test_cmd_check_invalid_expression_shows_error(captured):
    lines, fn = captured
    cmd_gradient_check(Args(expression="not valid"), print_fn=fn)
    combined = "\n".join(lines)
    assert "Error" in combined or "error" in combined


def test_cmd_score_prints_float(captured):
    lines, fn = captured
    cmd_gradient_score(Args(expression="*/10 * * * *"), print_fn=fn)
    assert len(lines) == 1
    float(lines[0])  # should not raise


def test_cmd_label_prints_label(captured):
    lines, fn = captured
    cmd_gradient_label(Args(expression="* * * * *"), print_fn=fn)
    assert lines[0] in ("smooth", "gradual", "uneven", "spiky")


def test_cmd_batch_prints_all_expressions(captured):
    lines, fn = captured
    exprs = ["* * * * *", "0 * * * *", "*/15 * * * *"]
    cmd_gradient_batch(Args(expressions=exprs), print_fn=fn)
    assert len(lines) == 3


def test_cmd_json_returns_valid_json(captured):
    lines, fn = captured
    cmd_gradient_json(Args(expression="*/5 * * * *"), print_fn=fn)
    data = json.loads("\n".join(lines))
    assert "expression" in data
    assert "score" in data
    assert "label" in data
    assert "deltas" in data


def test_cmd_json_invalid_has_error_key(captured):
    lines, fn = captured
    cmd_gradient_json(Args(expression="bad"), print_fn=fn)
    data = json.loads("\n".join(lines))
    assert data["error"] is not None
