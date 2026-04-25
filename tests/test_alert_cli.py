"""Tests for crontab_buddy.alert_cli module."""
import pytest
from crontab_buddy.alert_cli import (
    cmd_alert_set,
    cmd_alert_get,
    cmd_alert_delete,
    cmd_alert_list,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def tp(tmp_path):
    return str(tmp_path / "alerts.json")


def test_cmd_set_prints(tp, capsys):
    args = Args(expression="0 9 * * *", channel="email", event="failure", target=None)
    cmd_alert_set(args, path=tp)
    out = capsys.readouterr().out
    assert "Alert set" in out
    assert "email" in out


def test_cmd_set_invalid_channel_prints_error(tp, capsys):
    args = Args(expression="0 9 * * *", channel="fax", event="failure", target=None)
    cmd_alert_set(args, path=tp)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_get_existing(tp, capsys):
    set_args = Args(expression="0 9 * * *", channel="slack", event="any", target="#ops")
    cmd_alert_set(set_args, path=tp)
    get_args = Args(expression="0 9 * * *")
    cmd_alert_get(get_args, path=tp)
    out = capsys.readouterr().out
    assert "slack" in out
    assert "any" in out
    assert "#ops" in out


def test_cmd_get_missing(tp, capsys):
    args = Args(expression="* * * * *")
    cmd_alert_get(args, path=tp)
    out = capsys.readouterr().out
    assert "No alert" in out


def test_cmd_delete_success(tp, capsys):
    set_args = Args(expression="0 9 * * *", channel="log", event="failure", target=None)
    cmd_alert_set(set_args, path=tp)
    del_args = Args(expression="0 9 * * *")
    cmd_alert_delete(del_args, path=tp)
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_delete_missing(tp, capsys):
    args = Args(expression="0 9 * * *")
    cmd_alert_delete(args, path=tp)
    out = capsys.readouterr().out
    assert "No alert found" in out


def test_cmd_list_empty(tp, capsys):
    cmd_alert_list(Args(), path=tp)
    out = capsys.readouterr().out
    assert "No alerts" in out


def test_cmd_list_shows_entries(tp, capsys):
    set_args = Args(expression="0 9 * * *", channel="email", event="failure", target=None)
    cmd_alert_set(set_args, path=tp)
    cmd_alert_list(Args(), path=tp)
    out = capsys.readouterr().out
    assert "0 9 * * *" in out
    assert "email" in out
