"""Tests for crontab_buddy.impact and crontab_buddy.impact_cli."""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from crontab_buddy.impact import ImpactResult, assess_impact
from crontab_buddy.impact_cli import cmd_impact_assess, cmd_impact_json, cmd_impact_level
from crontab_buddy.parser import CronParseError


# ---------------------------------------------------------------------------
# assess_impact
# ---------------------------------------------------------------------------

def test_assess_every_minute_is_high():
    result = assess_impact("* * * * *")
    assert result.level == "high"


def test_assess_every_minute_runs_per_day():
    result = assess_impact("* * * * *")
    assert result.runs_per_day == pytest.approx(1440, rel=0.05)


def test_assess_hourly_is_elevated():
    result = assess_impact("0 * * * *")
    assert result.level == "elevated"
    assert result.runs_per_day == pytest.approx(24, rel=0.05)


def test_assess_daily_is_elevated():
    result = assess_impact("0 9 * * *")
    assert result.level == "elevated"
    assert result.runs_per_day == pytest.approx(1, rel=0.05)


def test_assess_weekly_is_moderate():
    result = assess_impact("0 9 * * 1")
    assert result.level == "moderate"
    assert result.runs_per_week == pytest.approx(1, rel=0.05)


def test_assess_monthly_is_low():
    result = assess_impact("0 9 1 * *")
    assert result.level == "low"
    assert result.runs_per_month == pytest.approx(1, rel=0.1)


def test_assess_invalid_expression_raises():
    with pytest.raises(CronParseError):
        assess_impact("not a cron")


def test_impact_result_str_contains_level():
    result = assess_impact("0 * * * *")
    text = str(result)
    assert "elevated" in text
    assert "0 * * * *" in text


def test_impact_result_fields():
    result = assess_impact("*/5 * * * *")
    assert isinstance(result, ImpactResult)
    assert result.runs_per_day > 0
    assert result.runs_per_week > 0
    assert result.runs_per_month > 0
    assert result.interval_seconds is not None


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def _args(expression: str) -> SimpleNamespace:
    return SimpleNamespace(expression=expression)


def test_cmd_impact_assess_prints(capsys):
    cmd_impact_assess(_args("0 * * * *"))
    out = capsys.readouterr().out
    assert "elevated" in out
    assert "Runs/day" in out


def test_cmd_impact_assess_invalid_prints_error(capsys):
    cmd_impact_assess(_args("bad expr"))
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_impact_level_prints_level(capsys):
    cmd_impact_level(_args("* * * * *"))
    out = capsys.readouterr().out.strip()
    assert out == "high"


def test_cmd_impact_level_invalid_prints_error(capsys):
    cmd_impact_level(_args("bad"))
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_impact_json_valid(capsys):
    cmd_impact_json(_args("0 9 * * *"))
    data = json.loads(capsys.readouterr().out)
    assert "level" in data
    assert "runs_per_day" in data
    assert data["expression"] == "0 9 * * *"


def test_cmd_impact_json_invalid(capsys):
    cmd_impact_json(_args("nope"))
    data = json.loads(capsys.readouterr().out)
    assert "error" in data
