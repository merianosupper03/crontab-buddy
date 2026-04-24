"""Tests for crontab_buddy.lock and lock_cli."""

from __future__ import annotations

import pytest
from pathlib import Path

from crontab_buddy.lock import (
    lock_expression,
    unlock_expression,
    get_lock,
    is_locked,
    list_locks,
    clear_locks,
)
from crontab_buddy.lock_cli import (
    cmd_lock_add,
    cmd_lock_remove,
    cmd_lock_check,
    cmd_lock_list,
    cmd_lock_clear,
)


@pytest.fixture
def tmp_lock(tmp_path):
    return tmp_path / "locks.json"


def test_lock_new_expression(tmp_lock):
    assert lock_expression("* * * * *", path=tmp_lock) is True
    assert is_locked("* * * * *", path=tmp_lock) is True


def test_lock_duplicate_returns_false(tmp_lock):
    lock_expression("0 * * * *", path=tmp_lock)
    assert lock_expression("0 * * * *", path=tmp_lock) is False


def test_unlock_existing(tmp_lock):
    lock_expression("0 0 * * *", path=tmp_lock)
    assert unlock_expression("0 0 * * *", path=tmp_lock) is True
    assert is_locked("0 0 * * *", path=tmp_lock) is False


def test_unlock_missing_returns_false(tmp_lock):
    assert unlock_expression("5 5 * * *", path=tmp_lock) is False


def test_get_lock_returns_reason(tmp_lock):
    lock_expression("1 2 * * *", reason="maintenance", path=tmp_lock)
    info = get_lock("1 2 * * *", path=tmp_lock)
    assert info is not None
    assert info["reason"] == "maintenance"


def test_get_lock_missing_returns_none(tmp_lock):
    assert get_lock("9 9 9 9 *", path=tmp_lock) is None


def test_list_locks(tmp_lock):
    lock_expression("* * * * 1", path=tmp_lock)
    lock_expression("0 12 * * *", path=tmp_lock)
    locks = list_locks(path=tmp_lock)
    assert "* * * * 1" in locks
    assert "0 12 * * *" in locks


def test_clear_locks_returns_count(tmp_lock):
    lock_expression("* * * * *", path=tmp_lock)
    lock_expression("0 * * * *", path=tmp_lock)
    n = clear_locks(path=tmp_lock)
    assert n == 2
    assert list_locks(path=tmp_lock) == {}


# --- CLI ---

class Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def test_cmd_add_prints_locked(tmp_lock, capsys):
    cmd_lock_add(Args(expression="* * * * *", reason="", path=tmp_lock))
    out = capsys.readouterr().out
    assert "Locked" in out


def test_cmd_add_duplicate_message(tmp_lock, capsys):
    cmd_lock_add(Args(expression="* * * * *", reason="", path=tmp_lock))
    cmd_lock_add(Args(expression="* * * * *", reason="", path=tmp_lock))
    out = capsys.readouterr().out
    assert "Already locked" in out


def test_cmd_remove_success(tmp_lock, capsys):
    lock_expression("0 * * * *", path=tmp_lock)
    cmd_lock_remove(Args(expression="0 * * * *", path=tmp_lock))
    out = capsys.readouterr().out
    assert "Unlocked" in out


def test_cmd_check_locked(tmp_lock, capsys):
    lock_expression("0 0 * * *", reason="deploy", path=tmp_lock)
    cmd_lock_check(Args(expression="0 0 * * *", path=tmp_lock))
    out = capsys.readouterr().out
    assert "LOCKED" in out
    assert "deploy" in out


def test_cmd_list_empty(tmp_lock, capsys):
    cmd_lock_list(Args(path=tmp_lock))
    out = capsys.readouterr().out
    assert "No locked" in out


def test_cmd_clear_prints_count(tmp_lock, capsys):
    lock_expression("* * * * *", path=tmp_lock)
    cmd_lock_clear(Args(path=tmp_lock))
    out = capsys.readouterr().out
    assert "1" in out
