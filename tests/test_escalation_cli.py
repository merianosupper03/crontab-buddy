"""Tests for crontab_buddy.escalation_cli."""

import pytest
from crontab_buddy.escalation import set_escalation
from crontab_buddy.escalation_cli import (
    cmd_escalation_delete,
    cmd_escalation_get,
    cmd_escalation_list,
    cmd_escalation_set,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def tp(tmp_path):
    return str(tmp_path / "escalations.json")


def test_cmd_set_prints(tp, capsys):
    args = Args(expression="0 9 * * 1", level="high", channel="email", contact="ops@x.com", path=tp)
    cmd_escalation_set(args)
    out = capsys.readouterr().out
    assert "high" in out
    assert "email" in out
    assert "ops@x.com" in out


def test_cmd_set_invalid_level_prints_error(tp, capsys):
    args = Args(expression="0 9 * * 1", level="mega", channel="email", contact="ops@x.com", path=tp)
    cmd_escalation_set(args)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_set_invalid_channel_prints_error(tp, capsys):
    args = Args(expression="0 9 * * 1", level="high", channel="fax", contact="ops@x.com", path=tp)
    cmd_escalation_set(args)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_get_existing(tp, capsys):
    set_escalation("0 9 * * 1", "critical", "pagerduty", "oncall", path=tp)
    args = Args(expression="0 9 * * 1", path=tp)
    cmd_escalation_get(args)
    out = capsys.readouterr().out
    assert "critical" in out
    assert "pagerduty" in out
    assert "oncall" in out


def test_cmd_get_missing(tp, capsys):
    args = Args(expression="* * * * *", path=tp)
    cmd_escalation_get(args)
    out = capsys.readouterr().out
    assert "No escalation" in out


def test_cmd_delete_success(tp, capsys):
    set_escalation("0 0 * * *", "low", "slack", "#ops", path=tp)
    args = Args(expression="0 0 * * *", path=tp)
    cmd_escalation_delete(args)
    out = capsys.readouterr().out
    assert "deleted" in out.lower()


def test_cmd_delete_missing(tp, capsys):
    args = Args(expression="0 0 * * *", path=tp)
    cmd_escalation_delete(args)
    out = capsys.readouterr().out
    assert "No escalation" in out


def test_cmd_list_with_entries(tp, capsys):
    set_escalation("0 9 * * 1", "high", "email", "a@b.com", path=tp)
    args = Args(path=tp)
    cmd_escalation_list(args)
    out = capsys.readouterr().out
    assert "0 9 * * 1" in out
    assert "high" in out


def test_cmd_list_empty(tp, capsys):
    args = Args(path=tp)
    cmd_escalation_list(args)
    out = capsys.readouterr().out
    assert "No escalation" in out
