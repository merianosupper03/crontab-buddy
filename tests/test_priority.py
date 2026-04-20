"""Tests for crontab_buddy.priority."""
import pytest
from pathlib import Path
from crontab_buddy.priority import (
    set_priority,
    get_priority,
    delete_priority,
    list_priorities,
    filter_by_priority,
    VALID_LEVELS,
)


@pytest.fixture
def tmp_prio(tmp_path):
    return tmp_path / "priorities.json"


def test_set_and_get_priority(tmp_prio):
    set_priority("0 * * * *", "high", tmp_prio)
    assert get_priority("0 * * * *", tmp_prio) == "high"


def test_get_missing_returns_none(tmp_prio):
    assert get_priority("* * * * *", tmp_prio) is None


def test_invalid_level_raises(tmp_prio):
    with pytest.raises(ValueError, match="Invalid priority level"):
        set_priority("0 * * * *", "urgent", tmp_prio)


def test_all_valid_levels_accepted(tmp_prio):
    for i, level in enumerate(VALID_LEVELS):
        expr = f"{i} * * * *"
        set_priority(expr, level, tmp_prio)
        assert get_priority(expr, tmp_prio) == level


def test_overwrite_priority(tmp_prio):
    set_priority("0 0 * * *", "low", tmp_prio)
    set_priority("0 0 * * *", "critical", tmp_prio)
    assert get_priority("0 0 * * *", tmp_prio) == "critical"


def test_delete_existing(tmp_prio):
    set_priority("5 4 * * *", "medium", tmp_prio)
    result = delete_priority("5 4 * * *", tmp_prio)
    assert result is True
    assert get_priority("5 4 * * *", tmp_prio) is None


def test_delete_missing_returns_false(tmp_prio):
    assert delete_priority("9 9 9 9 *", tmp_prio) is False


def test_list_priorities_sorted_by_severity(tmp_prio):
    set_priority("1 * * * *", "low", tmp_prio)
    set_priority("2 * * * *", "critical", tmp_prio)
    set_priority("3 * * * *", "medium", tmp_prio)
    entries = list_priorities(tmp_prio)
    levels = [e["priority"] for e in entries]
    assert levels.index("critical") < levels.index("medium")
    assert levels.index("medium") < levels.index("low")


def test_list_priorities_empty(tmp_prio):
    assert list_priorities(tmp_prio) == []


def test_filter_by_priority(tmp_prio):
    set_priority("0 1 * * *", "high", tmp_prio)
    set_priority("0 2 * * *", "low", tmp_prio)
    set_priority("0 3 * * *", "high", tmp_prio)
    high_exprs = filter_by_priority("high", tmp_prio)
    assert "0 1 * * *" in high_exprs
    assert "0 3 * * *" in high_exprs
    assert "0 2 * * *" not in high_exprs


def test_filter_by_priority_no_match(tmp_prio):
    set_priority("0 0 * * *", "low", tmp_prio)
    assert filter_by_priority("critical", tmp_prio) == []
