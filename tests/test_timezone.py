"""Tests for crontab_buddy.timezone."""

from datetime import datetime, timezone
import pytest

from crontab_buddy.timezone import (
    convert_runs,
    format_runs,
    is_valid_timezone,
    local_timezone,
)

UTC = timezone.utc


def _utc(*args) -> datetime:
    return datetime(*args, tzinfo=UTC)


def test_convert_runs_known_timezone():
    runs = [_utc(2024, 6, 1, 12, 0, 0)]
    converted = convert_runs(runs, "America/New_York")
    assert len(converted) == 1
    # UTC-4 in summer (EDT)
    assert converted[0].hour == 8


def test_convert_runs_unknown_timezone_raises():
    with pytest.raises(ValueError, match="Unknown timezone"):
        convert_runs([_utc(2024, 1, 1, 0, 0, 0)], "Mars/Olympus")


def test_format_runs_no_timezone():
    runs = [_utc(2024, 3, 15, 9, 30, 0)]
    result = format_runs(runs)
    assert result == ["2024-03-15 09:30:00 UTC"]


def test_format_runs_with_timezone():
    runs = [_utc(2024, 6, 1, 12, 0, 0)]
    result = format_runs(runs, "America/New_York")
    assert len(result) == 1
    assert "America/New_York" in result[0]
    assert "08:00:00" in result[0]


def test_format_runs_multiple():
    runs = [_utc(2024, 1, 1, 0, i, 0) for i in range(3)]
    result = format_runs(runs)
    assert len(result) == 3
    assert all("UTC" in r for r in result)


def test_is_valid_timezone_known():
    assert is_valid_timezone("Europe/London") is True
    assert is_valid_timezone("Asia/Tokyo") is True
    assert is_valid_timezone("UTC") is True


def test_is_valid_timezone_unknown():
    assert is_valid_timezone("Fake/Zone") is False
    assert is_valid_timezone("") is False


def test_local_timezone_returns_string():
    tz = local_timezone()
    assert isinstance(tz, str)
    assert len(tz) > 0
