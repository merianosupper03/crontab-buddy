import pytest
from pathlib import Path
from crontab_buddy.collections import (
    add_to_collection, remove_from_collection,
    get_collection, list_collections, delete_collection
)


@pytest.fixture
def tmp_col(tmp_path):
    return tmp_path / "collections.json"


def test_add_and_get(tmp_col):
    add_to_collection("work", "0 9 * * 1-5", path=tmp_col)
    col = get_collection("work", path=tmp_col)
    assert "0 9 * * 1-5" in col


def test_add_duplicate_returns_false(tmp_col):
    add_to_collection("work", "0 9 * * 1-5", path=tmp_col)
    result = add_to_collection("work", "0 9 * * 1-5", path=tmp_col)
    assert result is False


def test_add_multiple_expressions(tmp_col):
    add_to_collection("misc", "* * * * *", path=tmp_col)
    add_to_collection("misc", "0 0 * * *", path=tmp_col)
    col = get_collection("misc", path=tmp_col)
    assert len(col) == 2


def test_remove_existing(tmp_col):
    add_to_collection("work", "0 9 * * 1-5", path=tmp_col)
    ok = remove_from_collection("work", "0 9 * * 1-5", path=tmp_col)
    assert ok is True
    assert get_collection("work", path=tmp_col) == []


def test_remove_missing_returns_false(tmp_col):
    result = remove_from_collection("work", "0 9 * * 1-5", path=tmp_col)
    assert result is False


def test_get_missing_collection_returns_none(tmp_col):
    assert get_collection("ghost", path=tmp_col) is None


def test_list_collections(tmp_col):
    add_to_collection("a", "* * * * *", path=tmp_col)
    add_to_collection("b", "0 0 * * *", path=tmp_col)
    names = list_collections(path=tmp_col)
    assert "a" in names and "b" in names


def test_delete_collection(tmp_col):
    add_to_collection("temp", "* * * * *", path=tmp_col)
    ok = delete_collection("temp", path=tmp_col)
    assert ok is True
    assert get_collection("temp", path=tmp_col) is None


def test_delete_missing_returns_false(tmp_col):
    assert delete_collection("nope", path=tmp_col) is False


def test_collection_name_case_insensitive(tmp_col):
    add_to_collection("Work", "* * * * *", path=tmp_col)
    col = get_collection("work", path=tmp_col)
    assert col is not None
