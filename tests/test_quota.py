"""Tests for crontab_buddy.quota."""

import pytest
from unittest.mock import patch

from crontab_buddy.quota import (
    set_quota,
    get_quota,
    delete_quota,
    list_quotas,
)


@pytest.fixture
def tmp_quota(tmp_path, monkeypatch):
    quota_file = tmp_path / "quota.json"
    monkeypatch.setattr("crontab_buddy.quota._QUOTA_FILE", str(quota_file))
    return quota_file


def test_set_and_get(tmp_quota):
    set_quota("0 * * * *", 10, "daily")
    result = get_quota("0 * * * *")
    assert result is not None
    assert result["max_runs"] == 10
    assert result["period"] == "daily"


def test_get_missing_returns_none(tmp_quota):
    assert get_quota("* * * * *") is None


def test_invalid_max_runs_raises(tmp_quota):
    with pytest.raises(ValueError, match="max_runs"):
        set_quota("0 * * * *", 0, "daily")


def test_invalid_period_raises(tmp_quota):
    with pytest.raises(ValueError, match="period"):
        set_quota("0 * * * *", 5, "minutely")


def test_all_valid_periods_accepted(tmp_quota):
    for period in ("hourly", "daily", "weekly", "monthly"):
        set_quota("0 * * * *", 1, period)
        q = get_quota("0 * * * *")
        assert q["period"] == period


def test_overwrite_quota(tmp_quota):
    set_quota("0 * * * *", 5, "daily")
    set_quota("0 * * * *", 99, "weekly")
    q = get_quota("0 * * * *")
    assert q["max_runs"] == 99
    assert q["period"] == "weekly"


def test_delete_existing(tmp_quota):
    set_quota("0 * * * *", 3, "hourly")
    assert delete_quota("0 * * * *") is True
    assert get_quota("0 * * * *") is None


def test_delete_missing_returns_false(tmp_quota):
    assert delete_quota("5 4 * * *") is False


def test_list_quotas_empty(tmp_quota):
    assert list_quotas() == {}


def test_list_quotas_multiple(tmp_quota):
    set_quota("0 * * * *", 10, "daily")
    set_quota("*/5 * * * *", 2, "hourly")
    result = list_quotas()
    assert len(result) == 2
    assert "0 * * * *" in result
    assert "*/5 * * * *" in result
