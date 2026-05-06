"""Tests for crontab_buddy.velocity_cli."""

from __future__ import annotations

import io
import sys
from unittest.mock import patch

import pytest

from crontab_buddy.velocity import VelocityResult
from crontab_buddy.velocity_cli import (
    cmd_velocity_check,
    cmd_velocity_level,
    cmd_velocity_rate,
    cmd_velocity_batch,
    cmd_velocity_json,
)


class Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


_RESULT = VelocityResult(
    expression="0 * * * *",
    window="24h",
    count=12,
    rate_per_hour=0.5,
    level="low",
)


def captured(fn, args):
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        fn(args)
    finally:
        sys.stdout = old
    return buf.getvalue()


def test_cmd_check_prints_expression():
    with patch("crontab_buddy.velocity_cli.compute_velocity", return_value=_RESULT):
        out = captured(cmd_velocity_check, Args(expression="0 * * * *", window="24h"))
    assert "0 * * * *" in out


def test_cmd_check_invalid_window_prints_error():
    with patch("crontab_buddy.velocity_cli.compute_velocity", side_effect=ValueError("Unknown window")):
        out = captured(cmd_velocity_check, Args(expression="0 * * * *", window="99y"))
    assert "Error" in out


def test_cmd_level_prints_level():
    with patch("crontab_buddy.velocity_cli.compute_velocity", return_value=_RESULT):
        out = captured(cmd_velocity_level, Args(expression="0 * * * *", window="24h"))
    assert "low" in out


def test_cmd_rate_prints_float():
    with patch("crontab_buddy.velocity_cli.compute_velocity", return_value=_RESULT):
        out = captured(cmd_velocity_rate, Args(expression="0 * * * *", window="24h"))
    assert "0.5" in out


def test_cmd_batch_prints_multiple():
    results = [
        VelocityResult("* * * * *", "24h", 1, 0.04, "low"),
        VelocityResult("0 * * * *", "24h", 0, 0.0, "idle"),
    ]
    with patch("crontab_buddy.velocity_cli.batch_velocity", return_value=results):
        out = captured(
            cmd_velocity_batch,
            Args(expressions=["* * * * *", "0 * * * *"], window="24h"),
        )
    assert "* * * * *" in out
    assert "0 * * * *" in out


def test_cmd_json_contains_keys():
    with patch("crontab_buddy.velocity_cli.compute_velocity", return_value=_RESULT):
        out = captured(cmd_velocity_json, Args(expression="0 * * * *", window="24h"))
    import json
    data = json.loads(out)
    assert "expression" in data
    assert "level" in data
    assert "rate_per_hour" in data


def test_cmd_json_error_on_bad_window():
    with patch("crontab_buddy.velocity_cli.compute_velocity", side_effect=ValueError("bad")):
        out = captured(cmd_velocity_json, Args(expression="0 * * * *", window="99y"))
    import json
    data = json.loads(out)
    assert "error" in data
