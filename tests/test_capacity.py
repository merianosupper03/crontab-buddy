"""Tests for crontab_buddy.capacity."""

import pytest
from crontab_buddy.capacity import (
    set_capacity,
    get_capacity,
    delete_capacity,
    list_capacities,
)


@pytest.fixture
def tmp_capacity(tmp_path):
    return str(tmp_path / "capacity.json")


def test_set_and_get(tmp_capacity):
    set_capacity("0 * * * *", 3, path=tmp_capacity)
    result = get_capacity("0 * * * *", path=tmp_capacity)
    assert result["max_slots"] == 3
    assert result["strategy"] == "drop"


def test_get_missing_returns_none(tmp_capacity):
    assert get_capacity("* * * * *", path=tmp_capacity) is None


def test_overwrite_capacity(tmp_capacity):
    set_capacity("0 * * * *", 2, strategy="queue", path=tmp_capacity)
    set_capacity("0 * * * *", 5, strategy="replace", path=tmp_capacity)
    result = get_capacity("0 * * * *", path=tmp_capacity)
    assert result["max_slots"] == 5
    assert result["strategy"] == "replace"


def test_delete_existing(tmp_capacity):
    set_capacity("0 * * * *", 1, path=tmp_capacity)
    assert delete_capacity("0 * * * *", path=tmp_capacity) is True
    assert get_capacity("0 * * * *", path=tmp_capacity) is None


def test_delete_missing_returns_false(tmp_capacity):
    assert delete_capacity("0 * * * *", path=tmp_capacity) is False


def test_list_capacities(tmp_capacity):
    set_capacity("0 * * * *", 2, path=tmp_capacity)
    set_capacity("*/5 * * * *", 4, strategy="queue", path=tmp_capacity)
    result = list_capacities(path=tmp_capacity)
    assert len(result) == 2
    assert "0 * * * *" in result
    assert "*/5 * * * *" in result


def test_invalid_max_slots_raises(tmp_capacity):
    with pytest.raises(ValueError, match="max_slots"):
        set_capacity("0 * * * *", 0, path=tmp_capacity)


def test_invalid_max_slots_string_raises(tmp_capacity):
    with pytest.raises(ValueError):
        set_capacity("0 * * * *", "lots", path=tmp_capacity)


def test_invalid_strategy_raises(tmp_capacity):
    with pytest.raises(ValueError, match="strategy"):
        set_capacity("0 * * * *", 2, strategy="ignore", path=tmp_capacity)


def test_all_valid_strategies_accepted(tmp_capacity):
    for strategy in ("drop", "queue", "replace"):
        set_capacity("0 * * * *", 1, strategy=strategy, path=tmp_capacity)
        result = get_capacity("0 * * * *", path=tmp_capacity)
        assert result["strategy"] == strategy
