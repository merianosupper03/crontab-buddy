"""Tests for crontab_buddy.evenness_cli."""
import json
from io import StringIO
from unittest.mock import patch
import pytest
from crontab_buddy.evenness_cli import (
    cmd_evenness_check,
    cmd_evenness_score,
    cmd_evenness_grade,
    cmd_evenness_batch,
    cmd_evenness_json,
)


class Args:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class captured:
    def __init__(self):
        self._buf = StringIO()

    def __enter__(self):
        self._patcher = patch("builtins.print", side_effect=lambda *a, **k: self._buf.write(" ".join(str(x) for x in a) + "\n"))
        self._patcher.start()
        return self

    def __exit__(self, *_):
        self._patcher.stop()

    @property
    def text(self):
        return self._buf.getvalue()


def test_cmd_check_prints_expression():
    args = Args(expression="*/5 * * * *")
    with captured() as cap:
        cmd_evenness_check(args)
    assert "*/5 * * * *" in cap.text


def test_cmd_check_prints_grade():
    args = Args(expression="*/5 * * * *")
    with captured() as cap:
        cmd_evenness_check(args)
    assert "perfectly even" in cap.text


def test_cmd_check_prints_score():
    args = Args(expression="*/5 * * * *")
    with captured() as cap:
        cmd_evenness_check(args)
    assert "Score" in cap.text


def test_cmd_check_invalid_expression_prints_error():
    args = Args(expression="bad expr")
    with captured() as cap:
        cmd_evenness_check(args)
    assert "Error" in cap.text or "error" in cap.text


def test_cmd_score_prints_float():
    args = Args(expression="* * * * *")
    with captured() as cap:
        cmd_evenness_score(args)
    assert "." in cap.text or "1" in cap.text


def test_cmd_grade_prints_label():
    args = Args(expression="* * * * *")
    with captured() as cap:
        cmd_evenness_grade(args)
    assert "even" in cap.text


def test_cmd_batch_prints_rows():
    args = Args(expressions=["* * * * *", "0 12 * * *"])
    with captured() as cap:
        cmd_evenness_batch(args)
    lines = [l for l in cap.text.strip().splitlines() if l]
    assert len(lines) == 2


def test_cmd_json_is_valid_json():
    args = Args(expression="*/10 * * * *")
    with captured() as cap:
        cmd_evenness_json(args)
    data = json.loads(cap.text)
    assert "score" in data
    assert "grade" in data
    assert "expression" in data


def test_cmd_json_error_field_none_for_valid():
    args = Args(expression="*/10 * * * *")
    with captured() as cap:
        cmd_evenness_json(args)
    data = json.loads(cap.text)
    assert data["error"] is None
