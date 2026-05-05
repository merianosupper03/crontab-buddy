"""Tests for crontab_buddy.forecast."""

from datetime import datetime
from unittest.mock import patch

import pytest

from crontab_buddy.forecast import forecast, format_forecast, WINDOW_OPTIONS


FIXED_NOW = datetime(2024, 1, 15, 12, 0, 0)


def test_window_options_keys():
    assert set(WINDOW_OPTIONS.keys()) == {"hour", "day", "week", "month"}


def test_forecast_invalid_expression():
    data = forecast("not valid at all", from_dt=FIXED_NOW)
    assert data["valid"] is False
    assert data["run_count"] == 0
    assert data["runs"] == []
    assert data["description"] is None


def test_forecast_every_minute_24h():
    data = forecast("* * * * *", window_hours=24, from_dt=FIXED_NOW)
    assert data["valid"] is True
    assert data["run_count"] == 24 * 60
    assert data["description"] is not None


def test_forecast_hourly_24h():
    data = forecast("0 * * * *", window_hours=24, from_dt=FIXED_NOW)
    assert data["valid"] is True
    assert data["run_count"] == 24


def test_forecast_daily_24h():
    data = forecast("0 9 * * *", window_hours=24, from_dt=FIXED_NOW)
    assert data["valid"] is True
    # only one 09:00 in a 24h window starting at 12:00 (next day)
    assert data["run_count"] == 1


def test_forecast_returns_datetime_objects():
    data = forecast("0 * * * *", window_hours=2, from_dt=FIXED_NOW)
    for r in data["runs"]:
        assert isinstance(r, datetime)


def test_forecast_runs_within_window():
    window_hours = 3
    data = forecast("0 * * * *", window_hours=window_hours, from_dt=FIXED_NOW)
    until = FIXED_NOW
    from datetime import timedelta
    until = FIXED_NOW + timedelta(hours=window_hours)
    for r in data["runs"]:
        assert r < until
        assert r >= FIXED_NOW


def test_format_forecast_invalid():
    data = forecast("bad expr", from_dt=FIXED_NOW)
    out = format_forecast(data)
    assert "Invalid" in out


def test_format_forecast_valid_contains_fields():
    data = forecast("0 9 * * *", window_hours=24, from_dt=FIXED_NOW)
    out = format_forecast(data)
    assert "Expression" in out
    assert "Description" in out
    assert "Run count" in out
    assert "Window" in out


def test_format_forecast_shows_next_runs():
    data = forecast("* * * * *", window_hours=1, from_dt=FIXED_NOW)
    out = format_forecast(data)
    assert "Next runs" in out


def test_format_forecast_truncates_at_five():
    data = forecast("* * * * *", window_hours=1, from_dt=FIXED_NOW)
    out = format_forecast(data)
    assert "more" in out
