"""Tests for crontab_buddy.budget_cli."""

import pytest

from crontab_buddy.budget_cli import (
    cmd_budget_delete,
    cmd_budget_get,
    cmd_budget_list,
    cmd_budget_set,
)


class Args:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@pytest.fixture()
def tp(tmp_path):
    return str(tmp_path / "budgets.json")


def test_cmd_set_prints(tp, capsys):
    args = Args(expression="0 * * * *", max_runs=50, period="daily", path=tp)
    cmd_budget_set(args)
    out = capsys.readouterr().out
    assert "Budget set" in out
    assert "50" in out
    assert "daily" in out


def test_cmd_set_invalid_max_runs_prints_error(tp, capsys):
    args = Args(expression="0 * * * *", max_runs="abc", period="daily", path=tp)
    cmd_budget_set(args)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_set_invalid_period_prints_error(tp, capsys):
    args = Args(expression="0 * * * *", max_runs=10, period="yearly", path=tp)
    cmd_budget_set(args)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_get_existing(tp, capsys):
    from crontab_buddy.budget import set_budget
    set_budget("0 * * * *", 20, "hourly", path=tp)
    args = Args(expression="0 * * * *", path=tp)
    cmd_budget_get(args)
    out = capsys.readouterr().out
    assert "20" in out
    assert "hourly" in out


def test_cmd_get_missing(tp, capsys):
    args = Args(expression="5 5 * * *", path=tp)
    cmd_budget_get(args)
    out = capsys.readouterr().out
    assert "No budget" in out


def test_cmd_delete_success(tp, capsys):
    from crontab_buddy.budget import set_budget
    set_budget("0 * * * *", 5, "weekly", path=tp)
    args = Args(expression="0 * * * *", path=tp)
    cmd_budget_delete(args)
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_delete_missing(tp, capsys):
    args = Args(expression="1 1 * * *", path=tp)
    cmd_budget_delete(args)
    out = capsys.readouterr().out
    assert "No budget" in out


def test_cmd_list_empty(tp, capsys):
    args = Args(path=tp)
    cmd_budget_list(args)
    out = capsys.readouterr().out
    assert "No budgets" in out


def test_cmd_list_with_entries(tp, capsys):
    from crontab_buddy.budget import set_budget
    set_budget("0 * * * *", 10, "daily", path=tp)
    set_budget("5 4 * * *", 3, "monthly", path=tp)
    args = Args(path=tp)
    cmd_budget_list(args)
    out = capsys.readouterr().out
    assert "0 * * * *" in out
    assert "5 4 * * *" in out
