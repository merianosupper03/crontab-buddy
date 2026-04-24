"""Tests for crontab_buddy.variable_cli."""

from __future__ import annotations

import pytest
from pathlib import Path

from crontab_buddy.variable import set_variable
from crontab_buddy.variable_cli import (
    cmd_variable_delete,
    cmd_variable_expand,
    cmd_variable_get,
    cmd_variable_list,
    cmd_variable_set,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.path = kwargs.get("path")


@pytest.fixture
def tp(tmp_path):
    return str(tmp_path / "variables.json")


def test_cmd_set_prints(tp, capsys):
    args = Args(name="hourly", expression="0 * * * *", path=tp)
    cmd_variable_set(args)
    out = capsys.readouterr().out
    assert "HOURLY" in out
    assert "0 * * * *" in out


def test_cmd_get_existing(tp, capsys):
    set_variable("daily", "0 0 * * *", path=Path(tp))
    args = Args(name="daily", path=tp)
    cmd_variable_get(args)
    out = capsys.readouterr().out
    assert "DAILY" in out
    assert "0 0 * * *" in out


def test_cmd_get_missing(tp, capsys):
    args = Args(name="ghost", path=tp)
    cmd_variable_get(args)
    out = capsys.readouterr().out
    assert "not found" in out.lower() or "no variable" in out.lower()


def test_cmd_delete_existing(tp, capsys):
    set_variable("temp", "* * * * *", path=Path(tp))
    args = Args(name="temp", path=tp)
    cmd_variable_delete(args)
    out = capsys.readouterr().out
    assert "deleted" in out.lower()


def test_cmd_delete_missing(tp, capsys):
    args = Args(name="ghost", path=tp)
    cmd_variable_delete(args)
    out = capsys.readouterr().out
    assert "not found" in out.lower()


def test_cmd_list_empty(tp, capsys):
    args = Args(path=tp)
    cmd_variable_list(args)
    out = capsys.readouterr().out
    assert "no variables" in out.lower()


def test_cmd_list_shows_entries(tp, capsys):
    set_variable("weekly", "0 0 * * 0", path=Path(tp))
    args = Args(path=tp)
    cmd_variable_list(args)
    out = capsys.readouterr().out
    assert "WEEKLY" in out
    assert "0 0 * * 0" in out


def test_cmd_expand_found(tp, capsys):
    set_variable("ev", "*/5 * * * *", path=Path(tp))
    args = Args(name="ev", path=tp)
    cmd_variable_expand(args)
    out = capsys.readouterr().out
    assert "*/5 * * * *" in out


def test_cmd_expand_missing(tp, capsys):
    args = Args(name="nope", path=tp)
    cmd_variable_expand(args)
    out = capsys.readouterr().out
    assert "not found" in out.lower()
