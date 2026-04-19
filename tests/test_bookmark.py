"""Tests for bookmark module and CLI."""

import pytest
from unittest.mock import MagicMock
from crontab_buddy.bookmark import add_bookmark, get_bookmark, delete_bookmark, list_bookmarks
from crontab_buddy.bookmark_cli import cmd_bookmark_add, cmd_bookmark_get, cmd_bookmark_delete, cmd_bookmark_list


@pytest.fixture
def tmp_bm(tmp_path):
    return str(tmp_path / "bookmarks.json")


def test_add_and_get(tmp_bm):
    assert add_bookmark("daily", "0 9 * * *", path=tmp_bm) is True
    assert get_bookmark("daily", path=tmp_bm) == "0 9 * * *"


def test_add_duplicate_returns_false(tmp_bm):
    add_bookmark("daily", "0 9 * * *", path=tmp_bm)
    assert add_bookmark("daily", "0 10 * * *", path=tmp_bm) is False


def test_get_missing_returns_none(tmp_bm):
    assert get_bookmark("nope", path=tmp_bm) is None


def test_delete_existing(tmp_bm):
    add_bookmark("weekly", "0 0 * * 0", path=tmp_bm)
    assert delete_bookmark("weekly", path=tmp_bm) is True
    assert get_bookmark("weekly", path=tmp_bm) is None


def test_delete_missing_returns_false(tmp_bm):
    assert delete_bookmark("ghost", path=tmp_bm) is False


def test_list_bookmarks(tmp_bm):
    add_bookmark("b", "0 0 * * *", path=tmp_bm)
    add_bookmark("a", "* * * * *", path=tmp_bm)
    result = list_bookmarks(path=tmp_bm)
    assert len(result) == 2
    assert result[0]["name"] == "a"  # sorted


def test_name_case_insensitive(tmp_bm):
    add_bookmark("Daily", "0 9 * * *", path=tmp_bm)
    assert get_bookmark("daily", path=tmp_bm) == "0 9 * * *"


# CLI tests

def args(**kwargs):
    m = MagicMock()
    for k, v in kwargs.items():
        setattr(m, k, v)
    m.path = None
    return m


def test_cmd_add_prints_bookmarked(tmp_bm, capsys):
    a = args(name="lunch", expression="0 12 * * *")
    a.path = tmp_bm
    cmd_bookmark_add(a)
    out = capsys.readouterr().out
    assert "Bookmarked" in out
    assert "lunch" in out


def test_cmd_add_duplicate_message(tmp_bm, capsys):
    a = args(name="lunch", expression="0 12 * * *")
    a.path = tmp_bm
    cmd_bookmark_add(a)
    cmd_bookmark_add(a)
    out = capsys.readouterr().out
    assert "already exists" in out


def test_cmd_get_missing(tmp_bm, capsys):
    a = args(name="ghost")
    a.path = tmp_bm
    cmd_bookmark_get(a)
    assert "No bookmark" in capsys.readouterr().out


def test_cmd_list_empty(tmp_bm, capsys):
    a = MagicMock()
    a.path = tmp_bm
    cmd_bookmark_list(a)
    assert "No bookmarks" in capsys.readouterr().out


def test_cmd_delete_success(tmp_bm, capsys):
    add_bookmark("x", "* * * * *", path=tmp_bm)
    a = args(name="x")
    a.path = tmp_bm
    cmd_bookmark_delete(a)
    assert "Deleted" in capsys.readouterr().out
