"""Tests for crontab_buddy/category.py"""
import pytest
from pathlib import Path
from crontab_buddy.category import (
    add_to_category,
    remove_from_category,
    get_category,
    list_categories,
    delete_category,
)


@pytest.fixture
def tmp_cat(tmp_path):
    return tmp_path / "categories.json"


def test_add_and_get(tmp_cat):
    add_to_category("backup", "0 2 * * *", tmp_cat)
    assert "0 2 * * *" in get_category("backup", tmp_cat)


def test_add_duplicate_returns_false(tmp_cat):
    add_to_category("backup", "0 2 * * *", tmp_cat)
    result = add_to_category("backup", "0 2 * * *", tmp_cat)
    assert result is False


def test_add_multiple_expressions(tmp_cat):
    add_to_category("jobs", "0 * * * *", tmp_cat)
    add_to_category("jobs", "*/5 * * * *", tmp_cat)
    exprs = get_category("jobs", tmp_cat)
    assert len(exprs) == 2


def test_category_name_is_case_insensitive(tmp_cat):
    add_to_category("Backup", "0 2 * * *", tmp_cat)
    assert "0 2 * * *" in get_category("backup", tmp_cat)


def test_remove_existing(tmp_cat):
    add_to_category("cleanup", "0 3 * * 0", tmp_cat)
    result = remove_from_category("cleanup", "0 3 * * 0", tmp_cat)
    assert result is True
    assert get_category("cleanup", tmp_cat) == []


def test_remove_missing_returns_false(tmp_cat):
    result = remove_from_category("cleanup", "0 3 * * 0", tmp_cat)
    assert result is False


def test_remove_last_expression_deletes_category(tmp_cat):
    add_to_category("temp", "* * * * *", tmp_cat)
    remove_from_category("temp", "* * * * *", tmp_cat)
    assert "temp" not in list_categories(tmp_cat)


def test_list_categories_sorted(tmp_cat):
    add_to_category("zebra", "0 0 * * *", tmp_cat)
    add_to_category("alpha", "0 0 * * *", tmp_cat)
    cats = list_categories(tmp_cat)
    assert cats == sorted(cats)


def test_get_missing_category_returns_empty(tmp_cat):
    assert get_category("nonexistent", tmp_cat) == []


def test_delete_category(tmp_cat):
    add_to_category("temp", "0 0 * * *", tmp_cat)
    result = delete_category("temp", tmp_cat)
    assert result is True
    assert "temp" not in list_categories(tmp_cat)


def test_delete_missing_category_returns_false(tmp_cat):
    result = delete_category("ghost", tmp_cat)
    assert result is False
