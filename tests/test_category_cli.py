"""Tests for crontab_buddy/category_cli.py"""
import pytest
from unittest.mock import patch
from crontab_buddy.category_cli import (
    cmd_category_add,
    cmd_category_remove,
    cmd_category_list,
    cmd_category_delete,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def tp(tmp_path):
    p = tmp_path / "categories.json"
    with patch("crontab_buddy.category._DEFAULT_PATH", p):
        yield p


def test_cmd_add_prints_added(tp, capsys):
    cmd_category_add(Args(category="backup", expression="0 2 * * *"))
    out = capsys.readouterr().out
    assert "Added" in out
    assert "backup" in out


def test_cmd_add_duplicate_message(tp, capsys):
    cmd_category_add(Args(category="backup", expression="0 2 * * *"))
    cmd_category_add(Args(category="backup", expression="0 2 * * *"))
    out = capsys.readouterr().out
    assert "already in" in out


def test_cmd_remove_success(tp, capsys):
    cmd_category_add(Args(category="jobs", expression="*/5 * * * *"))
    cmd_category_remove(Args(category="jobs", expression="*/5 * * * *"))
    out = capsys.readouterr().out
    assert "Removed" in out


def test_cmd_remove_missing(tp, capsys):
    cmd_category_remove(Args(category="jobs", expression="*/5 * * * *"))
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_list_with_category(tp, capsys):
    cmd_category_add(Args(category="nightly", expression="0 0 * * *"))
    cmd_category_list(Args(category="nightly"))
    out = capsys.readouterr().out
    assert "0 0 * * *" in out


def test_cmd_list_empty_category(tp, capsys):
    cmd_category_list(Args(category="empty"))
    out = capsys.readouterr().out
    assert "empty or does not exist" in out


def test_cmd_list_all_categories(tp, capsys):
    cmd_category_add(Args(category="alpha", expression="0 1 * * *"))
    cmd_category_add(Args(category="beta", expression="0 2 * * *"))
    cmd_category_list(Args(category=None))
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out


def test_cmd_delete_existing(tp, capsys):
    cmd_category_add(Args(category="temp", expression="* * * * *"))
    cmd_category_delete(Args(category="temp"))
    out = capsys.readouterr().out
    assert "Deleted" in out


def test_cmd_delete_missing(tp, capsys):
    cmd_category_delete(Args(category="ghost"))
    out = capsys.readouterr().out
    assert "not found" in out
