"""Tests for crontab_buddy.throttle."""

import pytest
from pathlib import Path
from crontab_buddy.throttle import (
    set_throttle,
    get_throttle,
    delete_throttle,
    list_throttles,
)


@pytest.fixture
def tmp_throttle(tmp_path):
    return tmp_path / "throttle.json"


def test_set_and_get(tmp_throttle):
    set_throttle("0 * * * *", 5, "minutes", path=tmp_throttle)
    result = get_throttle("0 * * * *", path=tmp_throttle)
    assert result == {"interval": 5, "unit": "minutes"}


def test_get_missing_returns_none(tmp_throttle):
    assert get_throttle("* * * * *", path=tmp_throttle) is None


def test_overwrite_throttle(tmp_throttle):
    set_throttle("0 * * * *", 5, "minutes", path=tmp_throttle)
    set_throttle("0 * * * *", 2, "hours", path=tmp_throttle)
    result = get_throttle("0 * * * *", path=tmp_throttle)
    assert result == {"interval": 2, "unit": "hours"}


def test_delete_existing(tmp_throttle):
    set_throttle("0 * * * *", 1, "days", path=tmp_throttle)
    removed = delete_throttle("0 * * * *", path=tmp_throttle)
    assert removed is True
    assert get_throttle("0 * * * *", path=tmp_throttle) is None


def test_delete_missing_returns_false(tmp_throttle):
    assert delete_throttle("0 * * * *", path=tmp_throttle) is False


def test_list_throttles_empty(tmp_throttle):
    assert list_throttles(path=tmp_throttle) == {}


def test_list_throttles_multiple(tmp_throttle):
    set_throttle("0 * * * *", 5, "minutes", path=tmp_throttle)
    set_throttle("*/5 * * * *", 30, "seconds", path=tmp_throttle)
    result = list_throttles(path=tmp_throttle)
    assert len(result) == 2
    assert "0 * * * *" in result
    assert "*/5 * * * *" in result


def test_invalid_interval_raises(tmp_throttle):
    with pytest.raises(ValueError, match="positive"):
        set_throttle("0 * * * *", 0, "minutes", path=tmp_throttle)


def test_negative_interval_raises(tmp_throttle):
    with pytest.raises(ValueError):
        set_throttle("0 * * * *", -3, "hours", path=tmp_throttle)


def test_invalid_unit_raises(tmp_throttle):
    with pytest.raises(ValueError, match="unit"):
        set_throttle("0 * * * *", 5, "weeks", path=tmp_throttle)


def test_all_valid_units_accepted(tmp_throttle):
    from crontab_buddy.throttle import VALID_UNITS
    for i, unit in enumerate(VALID_UNITS):
        expr = f"{i} * * * *"
        set_throttle(expr, 1, unit, path=tmp_throttle)
        result = get_throttle(expr, path=tmp_throttle)
        assert result["unit"] == unit
