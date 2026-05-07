"""Tests for crontab_buddy.polarity_cli."""

import json
import pytest
from io import StringIO
from unittest.mock import patch
from crontab_buddy.polarity_cli import (
    cmd_polarity_check,
    cmd_polarity_score,
    cmd_polarity_label,
    cmd_polarity_batch,
    cmd_polarity_json,
)


class Args:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def captured(cmd, **kwargs):
    args = Args(**kwargs)
    with patch("builtins.print") as mock_print:
        cmd(args)
    return " ".join(str(c.args[0]) for c in mock_print.call_args_list)


def test_cmd_check_prints_expression():
    out = captured(cmd_polarity_check, expression="0 10 * * *")
    assert "0 10 * * *" in out


def test_cmd_check_prints_polarity():
    out = captured(cmd_polarity_check, expression="0 10 * * *")
    assert "daytime" in out


def test_cmd_score_prints_float():
    out = captured(cmd_polarity_score, expression="0 10 * * *")
    assert float(out.strip())


def test_cmd_score_invalid_prints_error():
    out = captured(cmd_polarity_score, expression="bad expr")
    assert "Error" in out


def test_cmd_label_prints_label():
    out = captured(cmd_polarity_label, expression="0 2 * * *")
    assert "nighttime" in out


def test_cmd_label_invalid_prints_error():
    out = captured(cmd_polarity_label, expression="not cron")
    assert "Error" in out


def test_cmd_batch_prints_multiple():
    args = Args(expressions=["0 9 * * *", "0 2 * * *"])
    lines = []
    with patch("builtins.print", side_effect=lambda x: lines.append(x)):
        cmd_polarity_batch(args)
    assert len(lines) == 2


def test_cmd_json_is_valid_json():
    args = Args(expression="0 12 * * *")
    outputs = []
    with patch("builtins.print", side_effect=lambda x: outputs.append(x)):
        cmd_polarity_json(args)
    data = json.loads("\n".join(outputs))
    assert "polarity" in data
    assert "score" in data
    assert data["expression"] == "0 12 * * *"


def test_cmd_json_error_expression():
    args = Args(expression="oops")
    outputs = []
    with patch("builtins.print", side_effect=lambda x: outputs.append(x)):
        cmd_polarity_json(args)
    data = json.loads("\n".join(outputs))
    assert data["polarity"] == "error"
    assert data["error"] is not None
