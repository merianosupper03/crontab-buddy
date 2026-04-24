"""Tests for crontab_buddy.rollback"""

import pytest
from crontab_buddy.rollback import (
    push_rollback,
    pop_rollback,
    peek_rollback,
    get_rollback_stack,
    clear_rollback,
    list_rollback_slots,
)


@pytest.fixture
def tmp_rb(tmp_path):
    return str(tmp_path / "rollback.json")


def test_push_and_peek(tmp_rb):
    push_rollback("job1", "* * * * *", path=tmp_rb)
    assert peek_rollback("job1", path=tmp_rb) == "* * * * *"


def test_push_multiple_peek_returns_latest(tmp_rb):
    push_rollback("job1", "0 * * * *", path=tmp_rb)
    push_rollback("job1", "5 * * * *", path=tmp_rb)
    assert peek_rollback("job1", path=tmp_rb) == "5 * * * *"


def test_pop_returns_latest(tmp_rb):
    push_rollback("job1", "0 * * * *", path=tmp_rb)
    push_rollback("job1", "5 * * * *", path=tmp_rb)
    result = pop_rollback("job1", path=tmp_rb)
    assert result == "5 * * * *"


def test_pop_removes_entry(tmp_rb):
    push_rollback("job1", "0 * * * *", path=tmp_rb)
    push_rollback("job1", "5 * * * *", path=tmp_rb)
    pop_rollback("job1", path=tmp_rb)
    assert peek_rollback("job1", path=tmp_rb) == "0 * * * *"


def test_pop_empty_returns_none(tmp_rb):
    assert pop_rollback("nonexistent", path=tmp_rb) is None


def test_peek_empty_returns_none(tmp_rb):
    assert peek_rollback("nonexistent", path=tmp_rb) is None


def test_get_rollback_stack_order(tmp_rb):
    push_rollback("job1", "0 * * * *", path=tmp_rb)
    push_rollback("job1", "5 * * * *", path=tmp_rb)
    stack = get_rollback_stack("job1", path=tmp_rb)
    assert len(stack) == 2
    assert stack[0]["expression"] == "0 * * * *"
    assert stack[1]["expression"] == "5 * * * *"


def test_get_rollback_stack_has_timestamp(tmp_rb):
    push_rollback("job1", "* * * * *", path=tmp_rb)
    stack = get_rollback_stack("job1", path=tmp_rb)
    assert "timestamp" in stack[0]


def test_clear_existing(tmp_rb):
    push_rollback("job1", "* * * * *", path=tmp_rb)
    result = clear_rollback("job1", path=tmp_rb)
    assert result is True
    assert get_rollback_stack("job1", path=tmp_rb) == []


def test_clear_missing_returns_false(tmp_rb):
    assert clear_rollback("ghost", path=tmp_rb) is False


def test_list_rollback_slots(tmp_rb):
    push_rollback("alpha", "* * * * *", path=tmp_rb)
    push_rollback("beta", "0 9 * * *", path=tmp_rb)
    slots = list_rollback_slots(path=tmp_rb)
    assert "alpha" in slots
    assert "beta" in slots


def test_list_rollback_slots_empty(tmp_rb):
    assert list_rollback_slots(path=tmp_rb) == []


def test_multiple_slots_independent(tmp_rb):
    push_rollback("a", "* * * * *", path=tmp_rb)
    push_rollback("b", "0 0 * * *", path=tmp_rb)
    pop_rollback("a", path=tmp_rb)
    assert peek_rollback("a", path=tmp_rb) is None
    assert peek_rollback("b", path=tmp_rb) == "0 0 * * *"
