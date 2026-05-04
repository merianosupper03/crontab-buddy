"""Tests for crontab_buddy.lifecycle_cli."""

import pytest
from unittest.mock import patch

from crontab_buddy import lifecycle as lc
from crontab_buddy import lifecycle_cli as cli


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def tp(tmp_path, monkeypatch):
    path = str(tmp_path / "lifecycle.json")
    monkeypatch.setattr(lc, "_DATA_FILE", path)
    return path


def test_cmd_set_prints(tp, capsys):
    args = Args(expression="0 * * * *", state="active", reason=None)
    cli.cmd_lifecycle_set(args)
    out = capsys.readouterr().out
    assert "active" in out
    assert "0 * * * *" in out


def test_cmd_set_invalid_state_prints_error(tp, capsys):
    args = Args(expression="0 * * * *", state="zombie", reason=None)
    cli.cmd_lifecycle_set(args)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_get_existing(tp, capsys):
    lc.set_lifecycle("0 * * * *", "draft", reason="just created")
    args = Args(expression="0 * * * *")
    cli.cmd_lifecycle_get(args)
    out = capsys.readouterr().out
    assert "draft" in out
    assert "just created" in out


def test_cmd_get_missing(tp, capsys):
    args = Args(expression="1 2 3 4 5")
    cli.cmd_lifecycle_get(args)
    out = capsys.readouterr().out
    assert "No lifecycle info" in out


def test_cmd_delete_existing(tp, capsys):
    lc.set_lifecycle("0 * * * *", "active")
    args = Args(expression="0 * * * *")
    cli.cmd_lifecycle_delete(args)
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_delete_missing(tp, capsys):
    args = Args(expression="0 * * * *")
    cli.cmd_lifecycle_delete(args)
    out = capsys.readouterr().out
    assert "No lifecycle info found" in out


def test_cmd_list_all(tp, capsys):
    lc.set_lifecycle("0 * * * *", "active")
    lc.set_lifecycle("0 0 * * *", "retired")
    args = Args(state=None)
    cli.cmd_lifecycle_list(args)
    out = capsys.readouterr().out
    assert "ACTIVE" in out
    assert "RETIRED" in out


def test_cmd_list_by_state(tp, capsys):
    lc.set_lifecycle("0 * * * *", "draft")
    lc.set_lifecycle("0 0 * * *", "active")
    args = Args(state="draft")
    cli.cmd_lifecycle_list(args)
    out = capsys.readouterr().out
    assert "DRAFT" in out
    assert "ACTIVE" not in out


def test_cmd_list_empty(tp, capsys):
    args = Args(state=None)
    cli.cmd_lifecycle_list(args)
    out = capsys.readouterr().out
    assert "No lifecycle entries" in out
