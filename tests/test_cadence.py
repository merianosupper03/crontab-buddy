"""Tests for crontab_buddy.cadence and cadence_cli."""

import json
import pytest
from unittest.mock import patch
from crontab_buddy.cadence import classify_cadence, cadence_summary, format_cadence
from crontab_buddy.cadence_cli import (
    cmd_cadence_check,
    cmd_cadence_summary,
    cmd_cadence_format,
    cmd_cadence_json,
)


class Args:
    def __init__(self, expression):
        self.expression = expression


# --- classify_cadence ---

def test_every_minute_is_burst():
    assert classify_cadence("* * * * *") == "burst"


def test_hourly_is_frequent():
    assert classify_cadence("0 * * * *") == "frequent"


def test_daily_is_regular():
    assert classify_cadence("0 9 * * *") == "regular"


def test_weekly_is_infrequent():
    assert classify_cadence("0 9 * * 1") == "infrequent"


def test_monthly_is_rare():
    assert classify_cadence("0 9 1 * *") == "rare"


def test_invalid_expression_returns_unknown():
    assert classify_cadence("not a cron") == "unknown"


# --- cadence_summary ---

def test_summary_has_required_keys():
    result = cadence_summary("0 9 * * *")
    assert "expression" in result
    assert "cadence" in result
    assert "interval_seconds" in result
    assert "recurrence" in result


def test_summary_expression_matches_input():
    result = cadence_summary("0 9 * * *")
    assert result["expression"] == "0 9 * * *"


def test_summary_invalid_expression():
    result = cadence_summary("bad expr")
    assert result["cadence"] == "unknown"


# --- format_cadence ---

def test_format_cadence_contains_expression():
    result = format_cadence("0 * * * *")
    assert "0 * * * *" in result


def test_format_cadence_contains_cadence_level():
    result = format_cadence("0 * * * *")
    assert "frequent" in result


def test_format_cadence_unknown_for_invalid():
    result = format_cadence("nope")
    assert "unknown" in result


# --- CLI commands ---

def test_cmd_cadence_check_prints_level():
    out = []
    cmd_cadence_check(Args("* * * * *"), print_fn=out.append)
    assert any("burst" in line for line in out)


def test_cmd_cadence_summary_prints_fields():
    out = []
    cmd_cadence_summary(Args("0 9 * * *"), print_fn=out.append)
    combined = " ".join(out)
    assert "Cadence" in combined
    assert "Recurrence" in combined
    assert "Interval" in combined


def test_cmd_cadence_format_prints_string():
    out = []
    cmd_cadence_format(Args("0 9 * * *"), print_fn=out.append)
    assert len(out) == 1
    assert "0 9 * * *" in out[0]


def test_cmd_cadence_json_is_valid_json():
    out = []
    cmd_cadence_json(Args("0 9 * * *"), print_fn=out.append)
    data = json.loads(out[0])
    assert "cadence" in data
    assert "expression" in data
