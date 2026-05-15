"""Tests for density_cli commands."""

import json
import pytest
from io import StringIO
from unittest.mock import patch

from crontab_buddy.density_cli import (
    cmd_density_check,
    cmd_density_label,
    cmd_density_fires,
    cmd_density_batch,
    cmd_density_json,
)


class Args:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@pytest.fixture()
def captured(capsys):
    return capsys


def test_cmd_check_prints_expression(captured):
    args = Args(expression="* * * * *", window="24h")
    cmd_density_check(args)
    out = captured.readouterr().out
    assert "* * * * *" in out


def test_cmd_check_prints_label(captured):
    args = Args(expression="* * * * *", window="24h")
    cmd_density_check(args)
    out = captured.readouterr().out
    assert "Label" in out


def test_cmd_check_prints_fires(captured):
    args = Args(expression="* * * * *", window="24h")
    cmd_density_check(args)
    out = captured.readouterr().out
    assert "Fires" in out


def test_cmd_label_prints_string(captured):
    args = Args(expression="0 * * * *", window="24h")
    cmd_density_label(args)
    out = captured.readouterr().out.strip()
    assert len(out) > 0


def test_cmd_fires_prints_integer(captured):
    args = Args(expression="0 12 * * *", window="24h")
    cmd_density_fires(args)
    out = captured.readouterr().out.strip()
    assert out.isdigit()


def test_cmd_batch_prints_each_expression(captured):
    args = Args(expressions=["* * * * *", "0 12 * * *"], window="24h")
    cmd_density_batch(args)
    out = captured.readouterr().out
    assert "* * * * *" in out
    assert "0 12 * * *" in out


def test_cmd_json_valid_json(captured):
    args = Args(expression="*/5 * * * *", window="24h")
    cmd_density_json(args)
    out = captured.readouterr().out
    data = json.loads(out)
    assert "fires" in data
    assert "label" in data
    assert "windows" in data


def test_cmd_json_contains_expression(captured):
    args = Args(expression="0 0 * * 1", window="24h")
    cmd_density_json(args)
    out = captured.readouterr().out
    data = json.loads(out)
    assert "0 0 * * 1" in data["expressions"]
