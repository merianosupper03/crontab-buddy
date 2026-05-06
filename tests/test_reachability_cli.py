"""Tests for crontab_buddy.reachability_cli."""

from __future__ import annotations

import json
from io import StringIO
from unittest.mock import patch

import pytest

from crontab_buddy.reachability_cli import (
    cmd_reachability_batch,
    cmd_reachability_check,
    cmd_reachability_json,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


# ---------------------------------------------------------------------------
# cmd_reachability_check
# ---------------------------------------------------------------------------

def test_cmd_check_prints_output(capsys):
    args = Args(expression="* * * * *", start=None, end=None, window=1)
    cmd_reachability_check(args)
    out = capsys.readouterr().out
    assert "* * * * *" in out


def test_cmd_check_reachable_label(capsys):
    args = Args(expression="* * * * *", start=None, end=None, window=1)
    cmd_reachability_check(args)
    out = capsys.readouterr().out
    assert "REACHABLE" in out


def test_cmd_check_invalid_expression(capsys):
    args = Args(expression="99 99 99 99 99", start=None, end=None, window=1)
    cmd_reachability_check(args)
    out = capsys.readouterr().out
    assert "UNREACHABLE" in out


def test_cmd_check_with_start_string(capsys):
    args = Args(expression="* * * * *", start="2030-01-01", end=None, window=1)
    cmd_reachability_check(args)
    out = capsys.readouterr().out
    assert "* * * * *" in out


# ---------------------------------------------------------------------------
# cmd_reachability_batch
# ---------------------------------------------------------------------------

def test_cmd_batch_prints_summary(capsys):
    args = Args(expressions=["* * * * *", "0 0 * * *"], window=30)
    cmd_reachability_batch(args)
    out = capsys.readouterr().out
    assert "Summary" in out


def test_cmd_batch_counts_reachable(capsys):
    args = Args(expressions=["* * * * *", "bad"], window=30)
    cmd_reachability_batch(args)
    out = capsys.readouterr().out
    assert "1/2" in out


# ---------------------------------------------------------------------------
# cmd_reachability_json
# ---------------------------------------------------------------------------

def test_cmd_json_valid_json(capsys):
    args = Args(expression="* * * * *", window=1)
    cmd_reachability_json(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "reachable" in data


def test_cmd_json_contains_expression(capsys):
    args = Args(expression="0 6 * * *", window=30)
    cmd_reachability_json(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["expression"] == "0 6 * * *"


def test_cmd_json_invalid_expression(capsys):
    args = Args(expression="bad expr", window=1)
    cmd_reachability_json(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["reachable"] is False
    assert data["error"] is not None
