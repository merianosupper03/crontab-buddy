"""Tests for crontab_buddy.budget."""

import pytest

from crontab_buddy.budget import (
    VALID_PERIODS,
    delete_budget,
    get_budget,
    list_budgets,
    set_budget,
)


@pytest.fixture()
def tmp_budget(tmp_path):
    return str(tmp_path / "budgets.json")


def test_set_and_get(tmp_budget):
    set_budget("0 * * * *", 100, "daily", path=tmp_budget)
    entry = get_budget("0 * * * *", path=tmp_budget)
    assert entry is not None
    assert entry["max_runs"] == 100
    assert entry["period"] == "daily"


def test_get_missing_returns_none(tmp_budget):
    assert get_budget("* * * * *", path=tmp_budget) is None


def test_overwrite_budget(tmp_budget):
    set_budget("0 * * * *", 50, "hourly", path=tmp_budget)
    set_budget("0 * * * *", 200, "weekly", path=tmp_budget)
    entry = get_budget("0 * * * *", path=tmp_budget)
    assert entry["max_runs"] == 200
    assert entry["period"] == "weekly"


def test_invalid_max_runs_raises(tmp_budget):
    with pytest.raises(ValueError, match="max_runs"):
        set_budget("0 * * * *", 0, "daily", path=tmp_budget)


def test_negative_max_runs_raises(tmp_budget):
    with pytest.raises(ValueError):
        set_budget("0 * * * *", -5, "daily", path=tmp_budget)


def test_invalid_period_raises(tmp_budget):
    with pytest.raises(ValueError, match="period"):
        set_budget("0 * * * *", 10, "yearly", path=tmp_budget)


def test_all_valid_periods_accepted(tmp_budget):
    for i, period in enumerate(VALID_PERIODS):
        expr = f"{i} * * * *"
        set_budget(expr, 1, period, path=tmp_budget)
        entry = get_budget(expr, path=tmp_budget)
        assert entry["period"] == period


def test_delete_existing(tmp_budget):
    set_budget("0 * * * *", 10, "daily", path=tmp_budget)
    result = delete_budget("0 * * * *", path=tmp_budget)
    assert result is True
    assert get_budget("0 * * * *", path=tmp_budget) is None


def test_delete_missing_returns_false(tmp_budget):
    assert delete_budget("5 5 * * *", path=tmp_budget) is False


def test_list_budgets_empty(tmp_budget):
    assert list_budgets(path=tmp_budget) == []


def test_list_budgets_multiple(tmp_budget):
    set_budget("0 * * * *", 10, "daily", path=tmp_budget)
    set_budget("5 4 * * *", 3, "weekly", path=tmp_budget)
    entries = list_budgets(path=tmp_budget)
    assert len(entries) == 2
    exprs = {e["expression"] for e in entries}
    assert "0 * * * *" in exprs
    assert "5 4 * * *" in exprs
