"""Tests for crontab_buddy.group"""

import pytest
from crontab_buddy.group import (
    create_group, add_to_group, remove_from_group,
    get_group, delete_group, list_groups
)


@pytest.fixture
def tmp_group(tmp_path):
    return str(tmp_path / "groups.json")


def test_create_group(tmp_group):
    assert create_group("work", tmp_group) is True
    assert get_group("work", tmp_group) == []


def test_create_duplicate_returns_false(tmp_group):
    create_group("work", tmp_group)
    assert create_group("work", tmp_group) is False


def test_create_is_case_insensitive(tmp_group):
    create_group("Work", tmp_group)
    assert get_group("work", tmp_group) == []


def test_add_to_group(tmp_group):
    create_group("daily", tmp_group)
    assert add_to_group("daily", "0 9 * * *", tmp_group) is True
    assert "0 9 * * *" in get_group("daily", tmp_group)


def test_add_creates_group_if_missing(tmp_group):
    assert add_to_group("new", "*/5 * * * *", tmp_group) is True
    assert get_group("new", tmp_group) == ["*/5 * * * *"]


def test_add_duplicate_returns_false(tmp_group):
    add_to_group("g", "0 0 * * *", tmp_group)
    assert add_to_group("g", "0 0 * * *", tmp_group) is False


def test_add_multiple_expressions(tmp_group):
    add_to_group("g", "0 9 * * *", tmp_group)
    add_to_group("g", "0 17 * * *", tmp_group)
    group = get_group("g", tmp_group)
    assert len(group) == 2


def test_remove_existing(tmp_group):
    add_to_group("g", "0 9 * * *", tmp_group)
    assert remove_from_group("g", "0 9 * * *", tmp_group) is True
    assert get_group("g", tmp_group) == []


def test_remove_missing_returns_false(tmp_group):
    create_group("g", tmp_group)
    assert remove_from_group("g", "0 9 * * *", tmp_group) is False


def test_get_missing_group_returns_none(tmp_group):
    assert get_group("nonexistent", tmp_group) is None


def test_delete_group(tmp_group):
    create_group("g", tmp_group)
    assert delete_group("g", tmp_group) is True
    assert get_group("g", tmp_group) is None


def test_delete_missing_returns_false(tmp_group):
    assert delete_group("ghost", tmp_group) is False


def test_list_groups(tmp_group):
    create_group("a", tmp_group)
    create_group("b", tmp_group)
    groups = list_groups(tmp_group)
    assert "a" in groups
    assert "b" in groups
