"""Tests for crontab_buddy.checkpoint_cli."""

import pytest
from crontab_buddy.checkpoint_cli import (
    cmd_checkpoint_save,
    cmd_checkpoint_get,
    cmd_checkpoint_delete,
    cmd_checkpoint_list,
    cmd_checkpoint_search,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def tp(tmp_path):
    return str(tmp_path / "cp.json")


def test_cmd_save_prints(tp, capsys):
    args = Args(name="myjob", expression="0 9 * * 1-5", note="")
    cmd_checkpoint_save(args, path=tp)
    out = capsys.readouterr().out
    assert "myjob" in out
    assert "0 9 * * 1-5" in out


def test_cmd_get_existing(tp, capsys):
    args_save = Args(name="check1", expression="30 6 * * *", note="morning")
    cmd_checkpoint_save(args_save, path=tp)
    args_get = Args(name="check1")
    cmd_checkpoint_get(args_get, path=tp)
    out = capsys.readouterr().out
    assert "30 6 * * *" in out
    assert "morning" in out


def test_cmd_get_missing(tp, capsys):
    args = Args(name="nope")
    cmd_checkpoint_get(args, path=tp)
    out = capsys.readouterr().out
    assert "No checkpoint" in out


def test_cmd_delete_success(tp, capsys):
    args_save = Args(name="del_me", expression="* * * * *", note="")
    cmd_checkpoint_save(args_save, path=tp)
    args_del = Args(name="del_me")
    cmd_checkpoint_delete(args_del, path=tp)
    out = capsys.readouterr().out
    assert "deleted" in out


def test_cmd_delete_missing(tp, capsys):
    args = Args(name="ghost")
    cmd_checkpoint_delete(args, path=tp)
    out = capsys.readouterr().out
    assert "No checkpoint" in out


def test_cmd_list_empty(tp, capsys):
    args = Args()
    cmd_checkpoint_list(args, path=tp)
    out = capsys.readouterr().out
    assert "No checkpoints" in out


def test_cmd_list_shows_entries(tp, capsys):
    cmd_checkpoint_save(Args(name="alpha", expression="0 1 * * *", note=""), path=tp)
    cmd_checkpoint_save(Args(name="beta", expression="0 2 * * *", note=""), path=tp)
    cmd_checkpoint_list(Args(), path=tp)
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out


def test_cmd_search_prints_match(tp, capsys):
    cmd_checkpoint_save(Args(name="weekly", expression="0 0 * * 0", note=""), path=tp)
    cmd_checkpoint_search(Args(query="weekly"), path=tp)
    out = capsys.readouterr().out
    assert "weekly" in out


def test_cmd_search_no_match(tp, capsys):
    cmd_checkpoint_search(Args(query="zzznomatch"), path=tp)
    out = capsys.readouterr().out
    assert "No checkpoints" in out
