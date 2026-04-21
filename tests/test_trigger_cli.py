"""Tests for crontab_buddy.trigger_cli module."""

import pytest
from crontab_buddy.trigger_cli import (
    cmd_trigger_set,
    cmd_trigger_get,
    cmd_trigger_delete,
    cmd_trigger_list,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def tp(tmp_path):
    return str(tmp_path / "triggers.json")


def test_cmd_set_prints(tp, capsys):
    args = Args(expression="0 9 * * *", event="success", condition=None, path=tp)
    cmd_trigger_set(args)
    out = capsys.readouterr().out
    assert "Trigger set" in out
    assert "success" in out


def test_cmd_set_invalid_event_prints_error(tp, capsys):
    args = Args(expression="0 9 * * *", event="bogus", condition=None, path=tp)
    cmd_trigger_set(args)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_get_existing(tp, capsys):
    set_args = Args(expression="0 12 * * *", event="failure", condition=None, path=tp)
    cmd_trigger_set(set_args)
    get_args = Args(expression="0 12 * * *", path=tp)
    cmd_trigger_get(get_args)
    out = capsys.readouterr().out
    assert "failure" in out


def test_cmd_get_missing(tp, capsys):
    args = Args(expression="1 1 1 1 1", path=tp)
    cmd_trigger_get(args)
    out = capsys.readouterr().out
    assert "No trigger found" in out


def test_cmd_delete_success(tp, capsys):
    set_args = Args(expression="*/10 * * * *", event="always", condition=None, path=tp)
    cmd_trigger_set(set_args)
    del_args = Args(expression="*/10 * * * *", path=tp)
    cmd_trigger_delete(del_args)
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_delete_missing(tp, capsys):
    args = Args(expression="0 0 1 1 *", path=tp)
    cmd_trigger_delete(args)
    out = capsys.readouterr().out
    assert "No trigger found" in out


def test_cmd_list_empty(tp, capsys):
    args = Args(path=tp)
    cmd_trigger_list(args)
    out = capsys.readouterr().out
    assert "No triggers" in out


def test_cmd_list_with_entries(tp, capsys):
    for expr, event in [("0 9 * * *", "success"), ("0 18 * * 1", "failure")]:
        cmd_trigger_set(Args(expression=expr, event=event, condition=None, path=tp))
    capsys.readouterr()
    cmd_trigger_list(Args(path=tp))
    out = capsys.readouterr().out
    assert "0 9 * * *" in out
    assert "0 18 * * 1" in out
