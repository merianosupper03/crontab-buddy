"""Tests for crontab_buddy/tags.py"""

import pytest
from crontab_buddy.tags import (
    add_tag, remove_tag, get_tags, find_by_tag, list_all_tags, clear_tags
)

EXPR1 = "0 9 * * 1"
EXPR2 = "*/5 * * * *"


@pytest.fixture
def tmp_tags(tmp_path):
    return str(tmp_path / "tags.json")


def test_add_and_get_tag(tmp_tags):
    add_tag(EXPR1, "work", path=tmp_tags)
    assert "work" in get_tags(EXPR1, path=tmp_tags)


def test_add_multiple_tags(tmp_tags):
    add_tag(EXPR1, "work", path=tmp_tags)
    add_tag(EXPR1, "weekly", path=tmp_tags)
    tags = get_tags(EXPR1, path=tmp_tags)
    assert "work" in tags
    assert "weekly" in tags


def test_no_duplicate_tags(tmp_tags):
    add_tag(EXPR1, "work", path=tmp_tags)
    add_tag(EXPR1, "work", path=tmp_tags)
    assert get_tags(EXPR1, path=tmp_tags).count("work") == 1


def test_remove_tag(tmp_tags):
    add_tag(EXPR1, "work", path=tmp_tags)
    result = remove_tag(EXPR1, "work", path=tmp_tags)
    assert result is True
    assert "work" not in get_tags(EXPR1, path=tmp_tags)


def test_remove_nonexistent_tag_returns_false(tmp_tags):
    result = remove_tag(EXPR1, "ghost", path=tmp_tags)
    assert result is False


def test_expression_removed_when_no_tags_left(tmp_tags):
    add_tag(EXPR1, "solo", path=tmp_tags)
    remove_tag(EXPR1, "solo", path=tmp_tags)
    all_tags = list_all_tags(path=tmp_tags)
    assert EXPR1 not in all_tags


def test_find_by_tag(tmp_tags):
    add_tag(EXPR1, "important", path=tmp_tags)
    add_tag(EXPR2, "important", path=tmp_tags)
    results = find_by_tag("important", path=tmp_tags)
    assert EXPR1 in results
    assert EXPR2 in results


def test_find_by_tag_no_match(tmp_tags):
    assert find_by_tag("nope", path=tmp_tags) == []


def test_list_all_tags(tmp_tags):
    add_tag(EXPR1, "work", path=tmp_tags)
    add_tag(EXPR2, "monitor", path=tmp_tags)
    all_tags = list_all_tags(path=tmp_tags)
    assert EXPR1 in all_tags
    assert EXPR2 in all_tags


def test_clear_tags(tmp_tags):
    add_tag(EXPR1, "work", path=tmp_tags)
    clear_tags(path=tmp_tags)
    assert list_all_tags(path=tmp_tags) == {}


def test_get_tags_empty(tmp_tags):
    assert get_tags(EXPR1, path=tmp_tags) == []
