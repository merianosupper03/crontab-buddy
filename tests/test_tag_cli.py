"""Tests for crontab_buddy/tag_cli.py"""

import pytest
from crontab_buddy.tag_cli import (
    cmd_tag_add, cmd_tag_remove, cmd_tag_list, cmd_tag_find, cmd_tag_all
)

EXPR = "0 12 * * *"


@pytest.fixture
def tp(tmp_path):
    return str(tmp_path / "tags.json")


def test_cmd_tag_add_prints(tp, capsys):
    cmd_tag_add(EXPR, "noon", path=tp)
    out = capsys.readouterr().out
    assert "noon" in out
    assert EXPR in out


def test_cmd_tag_remove_success(tp, capsys):
    cmd_tag_add(EXPR, "noon", path=tp)
    cmd_tag_remove(EXPR, "noon", path=tp)
    out = capsys.readouterr().out
    assert "Removed" in out


def test_cmd_tag_remove_missing(tp, capsys):
    cmd_tag_remove(EXPR, "ghost", path=tp)
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_tag_list_with_tags(tp, capsys):
    cmd_tag_add(EXPR, "daily", path=tp)
    cmd_tag_list(EXPR, path=tp)
    out = capsys.readouterr().out
    assert "daily" in out


def test_cmd_tag_list_empty(tp, capsys):
    cmd_tag_list(EXPR, path=tp)
    out = capsys.readouterr().out
    assert "No tags" in out


def test_cmd_tag_find_match(tp, capsys):
    cmd_tag_add(EXPR, "daily", path=tp)
    cmd_tag_find("daily", path=tp)
    out = capsys.readouterr().out
    assert EXPR in out


def test_cmd_tag_find_no_match(tp, capsys):
    cmd_tag_find("nope", path=tp)
    out = capsys.readouterr().out
    assert "No expressions" in out


def test_cmd_tag_all_empty(tp, capsys):
    cmd_tag_all(path=tp)
    out = capsys.readouterr().out
    assert "No tags" in out


def test_cmd_tag_all_populated(tp, capsys):
    cmd_tag_add(EXPR, "daily", path=tp)
    cmd_tag_all(path=tp)
    out = capsys.readouterr().out
    assert EXPR in out
    assert "daily" in out
