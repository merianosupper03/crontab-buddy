"""Tests for crontab_buddy.deadline and deadline_cli."""
from __future__ import annotations

import pytest
from pathlib import Path
from datetime import datetime, timedelta

from crontab_buddy.deadline import (
    set_deadline, get_deadline, delete_deadline, list_deadlines, is_overdue
)


@pytest.fixture
def tmp_deadline(tmp_path):
    return tmp_path / "deadlines.json"


def _future(days=1):
    return (datetime.now() + timedelta(days=days)).isoformat(timespec="seconds")


def _past(days=1):
    return (datetime.now() - timedelta(days=days)).isoformat(timespec="seconds")


def test_set_and_get(tmp_deadline):
    set_deadline("0 9 * * *", _future(), path=tmp_deadline)
    info = get_deadline("0 9 * * *", path=tmp_deadline)
    assert info is not None
    assert "deadline" in info


def test_get_missing_returns_none(tmp_deadline):
    assert get_deadline("* * * * *", path=tmp_deadline) is None


def test_overwrite_deadline(tmp_deadline):
    d1 = _future(1)
    d2 = _future(2)
    set_deadline("0 9 * * *", d1, path=tmp_deadline)
    set_deadline("0 9 * * *", d2, path=tmp_deadline)
    info = get_deadline("0 9 * * *", path=tmp_deadline)
    assert info["deadline"] == d2


def test_invalid_deadline_raises(tmp_deadline):
    with pytest.raises(ValueError, match="Invalid deadline"):
        set_deadline("0 9 * * *", "not-a-date", path=tmp_deadline)


def test_delete_existing(tmp_deadline):
    set_deadline("0 9 * * *", _future(), path=tmp_deadline)
    assert delete_deadline("0 9 * * *", path=tmp_deadline) is True
    assert get_deadline("0 9 * * *", path=tmp_deadline) is None


def test_delete_missing_returns_false(tmp_deadline):
    assert delete_deadline("0 9 * * *", path=tmp_deadline) is False


def test_is_overdue_future(tmp_deadline):
    set_deadline("0 9 * * *", _future(5), path=tmp_deadline)
    assert is_overdue("0 9 * * *", path=tmp_deadline) is False


def test_is_overdue_past(tmp_deadline):
    set_deadline("0 9 * * *", _past(1), path=tmp_deadline)
    assert is_overdue("0 9 * * *", path=tmp_deadline) is True


def test_is_overdue_missing_returns_none(tmp_deadline):
    assert is_overdue("* * * * *", path=tmp_deadline) is None


def test_list_deadlines_sorted(tmp_deadline):
    set_deadline("0 12 * * *", _future(3), path=tmp_deadline)
    set_deadline("0 9 * * *", _future(1), path=tmp_deadline)
    set_deadline("0 6 * * *", _future(2), path=tmp_deadline)
    entries = list_deadlines(path=tmp_deadline)
    deadlines = [e["deadline"] for e in entries]
    assert deadlines == sorted(deadlines)


def test_list_deadlines_empty(tmp_deadline):
    assert list_deadlines(path=tmp_deadline) == []


def test_set_deadline_with_note(tmp_deadline):
    set_deadline("0 9 * * *", _future(), note="important", path=tmp_deadline)
    info = get_deadline("0 9 * * *", path=tmp_deadline)
    assert info["note"] == "important"
