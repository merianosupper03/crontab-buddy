"""Tests for crontab_buddy.rollback_cli"""

import pytest
from crontab_buddy.rollback_cli import (
    cmd_rollback_push,
    cmd_rollback_pop,
    cmd_rollback_peek,
    cmd_rollback_list,
    cmd_rollback_clear,
    cmd_rollback_slots,
)
from crontab_buddy.rollback import push_rollback


class Args:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


@pytest.fixture
def tp(tmp_path):
    return str(tmp_path / "rb.json")


def test_cmd_push_prints(tp, capsys):
    args = Args(name="job1", expression="* * * * *", path=tp)
    cmd_rollback_push(args, )
    out = capsys.readouterr().out
    assert "job1" in out
    assert "* * * * *" in out


def test_cmd_pop_prints_expression(tp, capsys):
    push_rollback("job1", "0 9 * * *", path=tp)
    args = Args(name="job1", path=tp)
    cmd_rollback_pop(args)
    out = capsys.readouterr().out
    assert "0 9 * * *" in out


def test_cmd_pop_empty_message(tp, capsys):
    args = Args(name="empty", path=tp)
    cmd_rollback_pop(args)
    out = capsys.readouterr().out
    assert "empty" in out


def test_cmd_peek_prints_expression(tp, capsys):
    push_rollback("job1", "0 9 * * *", path=tp)
    args = Args(name="job1", path=tp)
    cmd_rollback_peek(args)
    out = capsys.readouterr().out
    assert "0 9 * * *" in out


def test_cmd_peek_empty_message(tp, capsys):
    args = Args(name="none", path=tp)
    cmd_rollback_peek(args)
    out = capsys.readouterr().out
    assert "empty" in out


def test_cmd_list_shows_entries(tp, capsys):
    push_rollback("job1", "* * * * *", path=tp)
    push_rollback("job1", "0 9 * * *", path=tp)
    args = Args(name="job1", path=tp)
    cmd_rollback_list(args)
    out = capsys.readouterr().out
    assert "* * * * *" in out
    assert "0 9 * * *" in out


def test_cmd_list_empty_message(tp, capsys):
    args = Args(name="ghost", path=tp)
    cmd_rollback_list(args)
    out = capsys.readouterr().out
    assert "No rollback" in out


def test_cmd_clear_success(tp, capsys):
    push_rollback("job1", "* * * * *", path=tp)
    args = Args(name="job1", path=tp)
    cmd_rollback_clear(args)
    out = capsys.readouterr().out
    assert "Cleared" in out


def test_cmd_clear_missing(tp, capsys):
    args = Args(name="ghost", path=tp)
    cmd_rollback_clear(args)
    out = capsys.readouterr().out
    assert "No rollback" in out


def test_cmd_slots_lists_names(tp, capsys):
    push_rollback("alpha", "* * * * *", path=tp)
    push_rollback("beta", "0 0 * * *", path=tp)
    args = Args(path=tp)
    cmd_rollback_slots(args)
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out


def test_cmd_slots_empty_message(tp, capsys):
    args = Args(path=tp)
    cmd_rollback_slots(args)
    out = capsys.readouterr().out
    assert "No rollback slots" in out
