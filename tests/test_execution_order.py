"""Tests for crontab_buddy.execution_order."""

import pytest
from crontab_buddy.execution_order import (
    add_to_queue,
    remove_from_queue,
    get_queue,
    move_up,
    move_down,
    list_queues,
    delete_queue,
)


@pytest.fixture
def tmp_q(tmp_path):
    return str(tmp_path / "exec_order.json")


def test_add_and_get(tmp_q):
    add_to_queue("main", "0 * * * *", path=tmp_q)
    assert get_queue("main", path=tmp_q) == ["0 * * * *"]


def test_add_duplicate_returns_false(tmp_q):
    add_to_queue("main", "0 * * * *", path=tmp_q)
    result = add_to_queue("main", "0 * * * *", path=tmp_q)
    assert result is False


def test_add_duplicate_not_duplicated(tmp_q):
    add_to_queue("main", "0 * * * *", path=tmp_q)
    add_to_queue("main", "0 * * * *", path=tmp_q)
    assert get_queue("main", path=tmp_q).count("0 * * * *") == 1


def test_add_multiple_preserves_order(tmp_q):
    add_to_queue("main", "0 * * * *", path=tmp_q)
    add_to_queue("main", "30 6 * * *", path=tmp_q)
    add_to_queue("main", "*/5 * * * *", path=tmp_q)
    assert get_queue("main", path=tmp_q) == ["0 * * * *", "30 6 * * *", "*/5 * * * *"]


def test_remove_existing(tmp_q):
    add_to_queue("main", "0 * * * *", path=tmp_q)
    result = remove_from_queue("main", "0 * * * *", path=tmp_q)
    assert result is True
    assert get_queue("main", path=tmp_q) == []


def test_remove_missing_returns_false(tmp_q):
    result = remove_from_queue("main", "0 * * * *", path=tmp_q)
    assert result is False


def test_move_up(tmp_q):
    add_to_queue("main", "0 * * * *", path=tmp_q)
    add_to_queue("main", "30 6 * * *", path=tmp_q)
    move_up("main", "30 6 * * *", path=tmp_q)
    assert get_queue("main", path=tmp_q)[0] == "30 6 * * *"


def test_move_up_first_returns_false(tmp_q):
    add_to_queue("main", "0 * * * *", path=tmp_q)
    result = move_up("main", "0 * * * *", path=tmp_q)
    assert result is False


def test_move_down(tmp_q):
    add_to_queue("main", "0 * * * *", path=tmp_q)
    add_to_queue("main", "30 6 * * *", path=tmp_q)
    move_down("main", "0 * * * *", path=tmp_q)
    assert get_queue("main", path=tmp_q)[0] == "30 6 * * *"


def test_move_down_last_returns_false(tmp_q):
    add_to_queue("main", "0 * * * *", path=tmp_q)
    result = move_down("main", "0 * * * *", path=tmp_q)
    assert result is False


def test_list_queues(tmp_q):
    add_to_queue("alpha", "0 * * * *", path=tmp_q)
    add_to_queue("beta", "30 6 * * *", path=tmp_q)
    queues = list_queues(path=tmp_q)
    assert "alpha" in queues
    assert "beta" in queues


def test_queue_name_case_insensitive(tmp_q):
    add_to_queue("Main", "0 * * * *", path=tmp_q)
    assert get_queue("main", path=tmp_q) == ["0 * * * *"]


def test_delete_queue(tmp_q):
    add_to_queue("main", "0 * * * *", path=tmp_q)
    result = delete_queue("main", path=tmp_q)
    assert result is True
    assert get_queue("main", path=tmp_q) == []


def test_delete_missing_queue_returns_false(tmp_q):
    result = delete_queue("nonexistent", path=tmp_q)
    assert result is False
