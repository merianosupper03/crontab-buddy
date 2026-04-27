"""Tests for crontab_buddy.recurrence."""

import pytest
from crontab_buddy.recurrence import (
    detect_recurrence,
    recurrence_interval_seconds,
    is_high_frequency,
    describe_recurrence,
)


def test_detect_every_minute():
    assert detect_recurrence("* * * * *") == "every_minute"


def test_detect_hourly():
    assert detect_recurrence("0 * * * *") == "hourly"


def test_detect_daily():
    assert detect_recurrence("0 0 * * *") == "daily"


def test_detect_weekly():
    assert detect_recurrence("0 0 * * 0") == "weekly"


def test_detect_monthly():
    assert detect_recurrence("0 0 1 * *") == "monthly"


def test_detect_yearly():
    assert detect_recurrence("0 0 1 1 *") == "yearly"


def test_detect_custom_returns_none():
    assert detect_recurrence("15 4 * * 1-5") is None


def test_detect_invalid_expression_returns_none():
    assert detect_recurrence("not a cron") is None


def test_interval_every_minute():
    assert recurrence_interval_seconds("* * * * *") == 60


def test_interval_hourly():
    assert recurrence_interval_seconds("0 * * * *") == 3600


def test_interval_daily():
    assert recurrence_interval_seconds("0 0 * * *") == 86400


def test_interval_custom_returns_none():
    assert recurrence_interval_seconds("5 4 * * 1") is None


def test_is_high_frequency_every_minute():
    assert is_high_frequency("* * * * *") is True


def test_is_high_frequency_hourly_default_threshold():
    # 3600 >= 300, so not high frequency by default
    assert is_high_frequency("0 * * * *") is False


def test_is_high_frequency_custom_threshold():
    assert is_high_frequency("0 * * * *", threshold_seconds=7200) is True


def test_is_high_frequency_custom_expression_returns_false():
    assert is_high_frequency("15 4 * * 1-5") is False


def test_describe_every_minute():
    assert describe_recurrence("* * * * *") == "every minute"


def test_describe_daily():
    assert describe_recurrence("0 0 * * *") == "once per day"


def test_describe_custom_schedule():
    assert describe_recurrence("30 6 * * 1-5") == "custom schedule"


def test_describe_invalid_expression():
    assert describe_recurrence("bad expression") == "custom schedule"
