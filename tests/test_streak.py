import json
import os
from datetime import date, timedelta

import pytest

from crontab_buddy.streak import record_use, get_streak, list_streaks, reset_streak


@pytest.fixture
def tmp_streak(tmp_path):
    return str(tmp_path / "streaks.json")


def test_record_first_use(tmp_streak):
    record_use("0 9 * * 1", path=tmp_streak)
    info = get_streak("0 9 * * 1", path=tmp_streak)
    assert info is not None
    assert info["streak"] == 1
    assert info["total"] == 1
    assert info["last_date"] == date.today().isoformat()


def test_record_same_day_no_double_streak(tmp_streak):
    record_use("0 9 * * 1", path=tmp_streak)
    record_use("0 9 * * 1", path=tmp_streak)
    info = get_streak("0 9 * * 1", path=tmp_streak)
    assert info["streak"] == 1


def test_consecutive_day_increments_streak(tmp_streak):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    data = {"0 0 * * *": {"last_date": yesterday, "streak": 3, "total": 5}}
    with open(tmp_streak, "w") as f:
        json.dump(data, f)
    record_use("0 0 * * *", path=tmp_streak)
    info = get_streak("0 0 * * *", path=tmp_streak)
    assert info["streak"] == 4
    assert info["total"] == 6


def test_gap_resets_streak(tmp_streak):
    old_date = (date.today() - timedelta(days=3)).isoformat()
    data = {"* * * * *": {"last_date": old_date, "streak": 10, "total": 20}}
    with open(tmp_streak, "w") as f:
        json.dump(data, f)
    record_use("* * * * *", path=tmp_streak)
    info = get_streak("* * * * *", path=tmp_streak)
    assert info["streak"] == 1


def test_get_missing_returns_none(tmp_streak):
    assert get_streak("0 5 * * *", path=tmp_streak) is None


def test_list_streaks_sorted(tmp_streak):
    record_use("0 1 * * *", path=tmp_streak)
    data = {
        "0 1 * * *": {"last_date": date.today().isoformat(), "streak": 1, "total": 1},
        "0 2 * * *": {"last_date": date.today().isoformat(), "streak": 5, "total": 5},
    }
    with open(tmp_streak, "w") as f:
        json.dump(data, f)
    results = list_streaks(path=tmp_streak)
    assert results[0]["streak"] >= results[-1]["streak"]


def test_reset_streak_existing(tmp_streak):
    record_use("0 9 * * *", path=tmp_streak)
    removed = reset_streak("0 9 * * *", path=tmp_streak)
    assert removed is True
    assert get_streak("0 9 * * *", path=tmp_streak) is None


def test_reset_streak_missing(tmp_streak):
    assert reset_streak("nonexistent", path=tmp_streak) is False
