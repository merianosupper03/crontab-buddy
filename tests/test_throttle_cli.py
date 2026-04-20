"""Tests for crontab_buddy.throttle_cli."""

import pytest
from crontab_buddy.throttle_cli import (
    cmd_throttle_set,
    cmd_throttle_get,
    cmd_throttle_delete,
    cmd_throttle_list,
)


class Args:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@pytest.fixture
def tp(tmp_path):
    return tmp_path / "throttle.json"


def test_cmd_set_prints(tp, capsys):
    args = Args(expression="0 * * * *", interval=5, unit="minutes")
    cmd_throttle_set(args, path=tp)
    out = capsys.readouterr().out
    assert "0 * * * *" in out
    assert "5" in out
    assert "minutes" in out


def test_cmd_set_invalid_unit_prints_error(tp, capsys):
    args = Args(expression="0 * * * *", interval=5, unit="fortnights")
    cmd_throttle_set(args, path=tp)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_set_invalid_interval_prints_error(tp, capsys):
    args = Args(expression="0 * * * *", interval="abc", unit="minutes")
    cmd_throttle_set(args, path=tp)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_get_existing(tp, capsys):
    set_args = Args(expression="0 * * * *", interval=10, unit="hours")
    cmd_throttle_set(set_args, path=tp)
    get_args = Args(expression="0 * * * *")
    cmd_throttle_get(get_args, path=tp)
    out = capsys.readouterr().out
    assert "10" in out
    assert "hours" in out


def test_cmd_get_missing(tp, capsys):
    args = Args(expression="1 2 3 4 5")
    cmd_throttle_get(args, path=tp)
    out = capsys.readouterr().out
    assert "No throttle" in out


def test_cmd_delete_success(tp, capsys):
    set_args = Args(expression="0 * * * *", interval=1, unit="days")
    cmd_throttle_set(set_args, path=tp)
    del_args = Args(expression="0 * * * *")
    cmd_throttle_delete(del_args, path=tp)
    out = capsys.readouterr().out
    assert "removed" in out.lower()


def test_cmd_delete_missing(tp, capsys):
    args = Args(expression="9 9 9 9 9")
    cmd_throttle_delete(args, path=tp)
    out = capsys.readouterr().out
    assert "No throttle" in out


def test_cmd_list_empty(tp, capsys):
    from argparse import Namespace
    cmd_throttle_list(Namespace(), path=tp)
    out = capsys.readouterr().out
    assert "No throttles" in out


def test_cmd_list_shows_entries(tp, capsys):
    from argparse import Namespace
    set_args = Args(expression="0 * * * *", interval=3, unit="seconds")
    cmd_throttle_set(set_args, path=tp)
    cmd_throttle_list(Namespace(), path=tp)
    out = capsys.readouterr().out
    assert "0 * * * *" in out
    assert "3" in out
