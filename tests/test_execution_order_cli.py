"""Tests for crontab_buddy.execution_order_cli."""

import pytest
from crontab_buddy.execution_order import add_to_queue
from crontab_buddy.execution_order_cli import (
    cmd_queue_add,
    cmd_queue_remove,
    cmd_queue_list,
    cmd_queue_move_up,
    cmd_queue_move_down,
    cmd_queue_list_all,
    cmd_queue_delete,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def tp(tmp_path):
    return str(tmp_path / "exec_order.json")


def test_cmd_add_prints_added(tp, capsys):
    args = Args(queue="main", expression="0 * * * *", path=tp)
    cmd_queue_add(args)
    out = capsys.readouterr().out
    assert "Added" in out
    assert "0 * * * *" in out


def test_cmd_add_duplicate_message(tp, capsys):
    args = Args(queue="main", expression="0 * * * *", path=tp)
    cmd_queue_add(args)
    cmd_queue_add(args)
    out = capsys.readouterr().out
    assert "already" in out


def test_cmd_remove_success(tp, capsys):
    add_to_queue("main", "0 * * * *", path=tp)
    args = Args(queue="main", expression="0 * * * *", path=tp)
    cmd_queue_remove(args)
    out = capsys.readouterr().out
    assert "Removed" in out


def test_cmd_remove_missing(tp, capsys):
    args = Args(queue="main", expression="0 * * * *", path=tp)
    cmd_queue_remove(args)
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_list_shows_entries(tp, capsys):
    add_to_queue("main", "0 6 * * *", path=tp)
    args = Args(queue="main", path=tp)
    cmd_queue_list(args)
    out = capsys.readouterr().out
    assert "0 6 * * *" in out


def test_cmd_list_empty(tp, capsys):
    args = Args(queue="main", path=tp)
    cmd_queue_list(args)
    out = capsys.readouterr().out
    assert "empty" in out


def test_cmd_move_up_success(tp, capsys):
    add_to_queue("main", "0 * * * *", path=tp)
    add_to_queue("main", "30 6 * * *", path=tp)
    args = Args(queue="main", expression="30 6 * * *", path=tp)
    cmd_queue_move_up(args)
    out = capsys.readouterr().out
    assert "up" in out


def test_cmd_move_down_cannot(tp, capsys):
    add_to_queue("main", "0 * * * *", path=tp)
    args = Args(queue="main", expression="0 * * * *", path=tp)
    cmd_queue_move_down(args)
    out = capsys.readouterr().out
    assert "Cannot" in out


def test_cmd_list_all_shows_queues(tp, capsys):
    add_to_queue("alpha", "0 * * * *", path=tp)
    add_to_queue("beta", "30 6 * * *", path=tp)
    args = Args(path=tp)
    cmd_queue_list_all(args)
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out


def test_cmd_delete_queue(tp, capsys):
    add_to_queue("main", "0 * * * *", path=tp)
    args = Args(queue="main", path=tp)
    cmd_queue_delete(args)
    out = capsys.readouterr().out
    assert "Deleted" in out
