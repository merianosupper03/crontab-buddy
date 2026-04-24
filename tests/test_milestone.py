"""Tests for crontab_buddy.milestone."""

import pytest

from crontab_buddy.milestone import (
    set_milestone,
    get_milestone,
    mark_reached,
    delete_milestone,
    list_milestones,
)


@pytest.fixture
def tmp_ms(tmp_path):
    return str(tmp_path / "milestones.json")


def test_set_and_get(tmp_ms):
    set_milestone("0 * * * *", "first_100", 100, tmp_ms)
    m = get_milestone("0 * * * *", "first_100", tmp_ms)
    assert m is not None
    assert m["target"] == 100
    assert m["reached"] is False


def test_get_missing_returns_none(tmp_ms):
    assert get_milestone("0 * * * *", "ghost", tmp_ms) is None


def test_invalid_target_raises(tmp_ms):
    with pytest.raises(ValueError):
        set_milestone("0 * * * *", "bad", 0, tmp_ms)


def test_negative_target_raises(tmp_ms):
    with pytest.raises(ValueError):
        set_milestone("0 * * * *", "bad", -5, tmp_ms)


def test_overwrite_milestone(tmp_ms):
    set_milestone("0 * * * *", "goal", 50, tmp_ms)
    set_milestone("0 * * * *", "goal", 200, tmp_ms)
    m = get_milestone("0 * * * *", "goal", tmp_ms)
    assert m["target"] == 200


def test_mark_reached_existing(tmp_ms):
    set_milestone("0 * * * *", "first_100", 100, tmp_ms)
    result = mark_reached("0 * * * *", "first_100", tmp_ms)
    assert result is True
    m = get_milestone("0 * * * *", "first_100", tmp_ms)
    assert m["reached"] is True


def test_mark_reached_missing_returns_false(tmp_ms):
    assert mark_reached("0 * * * *", "nope", tmp_ms) is False


def test_delete_existing(tmp_ms):
    set_milestone("0 * * * *", "first_100", 100, tmp_ms)
    assert delete_milestone("0 * * * *", "first_100", tmp_ms) is True
    assert get_milestone("0 * * * *", "first_100", tmp_ms) is None


def test_delete_missing_returns_false(tmp_ms):
    assert delete_milestone("0 * * * *", "ghost", tmp_ms) is False


def test_list_milestones(tmp_ms):
    set_milestone("0 * * * *", "a", 10, tmp_ms)
    set_milestone("0 * * * *", "b", 50, tmp_ms)
    items = list_milestones("0 * * * *", tmp_ms)
    names = {i["name"] for i in items}
    assert names == {"a", "b"}


def test_list_milestones_empty(tmp_ms):
    assert list_milestones("0 * * * *", tmp_ms) == []


def test_expression_whitespace_stripped(tmp_ms):
    set_milestone("  0 * * * *  ", "ws", 5, tmp_ms)
    assert get_milestone("0 * * * *", "ws", tmp_ms) is not None
