"""Tests for crontab_buddy.saturation_cli."""
import io
import sys
import pytest
from crontab_buddy.saturation_cli import (
    cmd_saturation_check,
    cmd_saturation_grade,
    cmd_saturation_score,
    cmd_saturation_batch,
    cmd_saturation_json,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def captured(fn, *args, **kwargs):
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        fn(*args, **kwargs)
    finally:
        sys.stdout = old
    return buf.getvalue()


def test_cmd_check_prints_expression():
    out = captured(cmd_saturation_check, Args(expression="* * * * *"))
    assert "* * * * *" in out


def test_cmd_check_prints_overall():
    out = captured(cmd_saturation_check, Args(expression="* * * * *"))
    assert "Overall" in out


def test_cmd_check_invalid_expression_prints_error():
    out = captured(cmd_saturation_check, Args(expression="bad expr"))
    assert "Error" in out or "error" in out


def test_cmd_grade_saturated():
    out = captured(cmd_saturation_grade, Args(expression="* * * * *"))
    assert out.strip() == "saturated"


def test_cmd_grade_minimal():
    out = captured(cmd_saturation_grade, Args(expression="0 9 1 1 1"))
    assert out.strip() == "minimal"


def test_cmd_grade_invalid_prints_error():
    out = captured(cmd_saturation_grade, Args(expression="bad"))
    assert "error" in out


def test_cmd_score_all_wildcards_is_one():
    out = captured(cmd_saturation_score, Args(expression="* * * * *"))
    assert float(out.strip()) == pytest.approx(1.0)


def test_cmd_score_invalid_is_zero():
    out = captured(cmd_saturation_score, Args(expression="bad"))
    assert out.strip() == "0.0"


def test_cmd_batch_prints_all_expressions():
    exprs = ["* * * * *", "0 9 * * 1"]
    out = captured(cmd_saturation_batch, Args(expressions=exprs))
    assert "* * * * *" in out
    assert "0 9 * * 1" in out


def test_cmd_json_contains_grade():
    import json
    out = captured(cmd_saturation_json, Args(expression="* * * * *"))
    data = json.loads(out)
    assert "grade" in data
    assert data["grade"] == "saturated"


def test_cmd_json_contains_scores():
    import json
    out = captured(cmd_saturation_json, Args(expression="* * * * *"))
    data = json.loads(out)
    assert "scores" in data
    assert set(data["scores"].keys()) == {"minute", "hour", "dom", "month", "dow"}
