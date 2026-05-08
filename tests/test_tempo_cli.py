"""Tests for crontab_buddy.tempo_cli."""
import json
import pytest
from crontab_buddy.tempo_cli import (
    cmd_tempo_check,
    cmd_tempo_level,
    cmd_tempo_score,
    cmd_tempo_batch,
    cmd_tempo_json,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def captured():
    lines = []
    return lines, lambda msg: lines.append(msg)


def test_cmd_check_prints_expression(captured):
    lines, fn = captured
    cmd_tempo_check(Args(expression="* * * * *"), print_fn=fn)
    assert any("* * * * *" in l for l in lines)


def test_cmd_check_prints_level(captured):
    lines, fn = captured
    cmd_tempo_check(Args(expression="* * * * *"), print_fn=fn)
    assert any("frantic" in l for l in lines)


def test_cmd_check_prints_score(captured):
    lines, fn = captured
    cmd_tempo_check(Args(expression="* * * * *"), print_fn=fn)
    assert any("Score" in l for l in lines)


def test_cmd_check_invalid_prints_error(captured):
    lines, fn = captured
    cmd_tempo_check(Args(expression="not valid"), print_fn=fn)
    assert any("Error" in l for l in lines)


def test_cmd_level_prints_level(captured):
    lines, fn = captured
    cmd_tempo_level(Args(expression="* * * * *"), print_fn=fn)
    assert lines[0] == "frantic"


def test_cmd_score_prints_float(captured):
    lines, fn = captured
    cmd_tempo_score(Args(expression="* * * * *"), print_fn=fn)
    score = float(lines[0])
    assert 0.0 <= score <= 1.0


def test_cmd_batch_prints_rows(captured):
    lines, fn = captured
    cmd_tempo_batch(Args(expressions=["* * * * *", "0 * * * *"]), print_fn=fn)
    assert len(lines) == 2


def test_cmd_batch_invalid_shows_error(captured):
    lines, fn = captured
    cmd_tempo_batch(Args(expressions=["bad expr"]), print_fn=fn)
    assert any("ERROR" in l for l in lines)


def test_cmd_json_is_valid_json(captured):
    lines, fn = captured
    cmd_tempo_json(Args(expression="* * * * *"), print_fn=fn)
    data = json.loads("\n".join(lines))
    assert "level" in data
    assert "score" in data
    assert "expression" in data


def test_cmd_json_invalid_has_error_key(captured):
    lines, fn = captured
    cmd_tempo_json(Args(expression="bad"), print_fn=fn)
    data = json.loads("\n".join(lines))
    assert data["error"] is not None
