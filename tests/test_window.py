"""Tests for crontab_buddy.window."""

import pytest

from crontab_buddy.window import (
    set_window,
    get_window,
    delete_window,
    list_windows,
    is_within_window,
)

EXPR = "0 9 * * 1-5"


@pytest.fixture
def tmp_win(tmp_path):
    return str(tmp_path / "windows.json")


def test_set_and_get(tmp_win):
    set_window(EXPR, 9, 17, path=tmp_win)
    w = get_window(EXPR, path=tmp_win)
    assert w is not None
    assert w["start_hour"] == 9
    assert w["end_hour"] == 17


def test_get_missing_returns_none(tmp_win):
    assert get_window(EXPR, path=tmp_win) is None


def test_overwrite_window(tmp_win):
    set_window(EXPR, 8, 18, path=tmp_win)
    set_window(EXPR, 10, 20, path=tmp_win)
    w = get_window(EXPR, path=tmp_win)
    assert w["start_hour"] == 10
    assert w["end_hour"] == 20


def test_delete_existing(tmp_win):
    set_window(EXPR, 9, 17, path=tmp_win)
    assert delete_window(EXPR, path=tmp_win) is True
    assert get_window(EXPR, path=tmp_win) is None


def test_delete_missing_returns_false(tmp_win):
    assert delete_window(EXPR, path=tmp_win) is False


def test_list_windows_empty(tmp_win):
    assert list_windows(path=tmp_win) == {}


def test_list_windows_multiple(tmp_win):
    set_window(EXPR, 9, 17, path=tmp_win)
    set_window("*/5 * * * *", 0, 23, path=tmp_win)
    result = list_windows(path=tmp_win)
    assert len(result) == 2
    assert EXPR in result
    assert "*/5 * * * *" in result


def test_invalid_hour_out_of_range(tmp_win):
    with pytest.raises(ValueError, match="0 and 23"):
        set_window(EXPR, -1, 17, path=tmp_win)
    with pytest.raises(ValueError, match="0 and 23"):
        set_window(EXPR, 9, 24, path=tmp_win)


def test_start_not_less_than_end_raises(tmp_win):
    with pytest.raises(ValueError, match="less than"):
        set_window(EXPR, 17, 9, path=tmp_win)
    with pytest.raises(ValueError, match="less than"):
        set_window(EXPR, 12, 12, path=tmp_win)


def test_is_within_window_true(tmp_win):
    set_window(EXPR, 9, 17, path=tmp_win)
    assert is_within_window(EXPR, 9, path=tmp_win) is True
    assert is_within_window(EXPR, 13, path=tmp_win) is True
    assert is_within_window(EXPR, 17, path=tmp_win) is True


def test_is_within_window_false(tmp_win):
    set_window(EXPR, 9, 17, path=tmp_win)
    assert is_within_window(EXPR, 8, path=tmp_win) is False
    assert is_within_window(EXPR, 18, path=tmp_win) is False


def test_is_within_window_no_window_returns_true(tmp_win):
    assert is_within_window(EXPR, 3, path=tmp_win) is True
