"""Tests for crontab_buddy.metadata."""

import pytest
from crontab_buddy.metadata import (
    set_metadata,
    get_metadata,
    get_all_metadata,
    delete_metadata,
    clear_metadata,
    list_all_metadata,
)


@pytest.fixture
def tmp_meta(tmp_path):
    return str(tmp_path / "metadata.json")


def test_set_and_get(tmp_meta):
    set_metadata("0 * * * *", "owner", "alice", path=tmp_meta)
    assert get_metadata("0 * * * *", "owner", path=tmp_meta) == "alice"


def test_get_missing_key_returns_none(tmp_meta):
    assert get_metadata("0 * * * *", "missing", path=tmp_meta) is None


def test_get_missing_expression_returns_none(tmp_meta):
    assert get_metadata("*/5 * * * *", "owner", path=tmp_meta) is None


def test_overwrite_existing_key(tmp_meta):
    set_metadata("0 * * * *", "owner", "alice", path=tmp_meta)
    set_metadata("0 * * * *", "owner", "bob", path=tmp_meta)
    assert get_metadata("0 * * * *", "owner", path=tmp_meta) == "bob"


def test_multiple_keys_same_expression(tmp_meta):
    set_metadata("0 * * * *", "owner", "alice", path=tmp_meta)
    set_metadata("0 * * * *", "env", "prod", path=tmp_meta)
    meta = get_all_metadata("0 * * * *", path=tmp_meta)
    assert meta["owner"] == "alice"
    assert meta["env"] == "prod"


def test_get_all_metadata_empty(tmp_meta):
    assert get_all_metadata("0 * * * *", path=tmp_meta) == {}


def test_delete_existing_key(tmp_meta):
    set_metadata("0 * * * *", "owner", "alice", path=tmp_meta)
    result = delete_metadata("0 * * * *", "owner", path=tmp_meta)
    assert result is True
    assert get_metadata("0 * * * *", "owner", path=tmp_meta) is None


def test_delete_missing_key_returns_false(tmp_meta):
    result = delete_metadata("0 * * * *", "nope", path=tmp_meta)
    assert result is False


def test_delete_last_key_removes_expression(tmp_meta):
    set_metadata("0 * * * *", "owner", "alice", path=tmp_meta)
    delete_metadata("0 * * * *", "owner", path=tmp_meta)
    all_meta = list_all_metadata(path=tmp_meta)
    assert "0 * * * *" not in all_meta


def test_clear_metadata(tmp_meta):
    set_metadata("0 * * * *", "a", 1, path=tmp_meta)
    set_metadata("0 * * * *", "b", 2, path=tmp_meta)
    result = clear_metadata("0 * * * *", path=tmp_meta)
    assert result is True
    assert get_all_metadata("0 * * * *", path=tmp_meta) == {}


def test_clear_missing_expression_returns_false(tmp_meta):
    result = clear_metadata("*/15 * * * *", path=tmp_meta)
    assert result is False


def test_list_all_metadata(tmp_meta):
    set_metadata("0 * * * *", "owner", "alice", path=tmp_meta)
    set_metadata("*/5 * * * *", "env", "staging", path=tmp_meta)
    all_meta = list_all_metadata(path=tmp_meta)
    assert "0 * * * *" in all_meta
    assert "*/5 * * * *" in all_meta


def test_numeric_and_bool_values(tmp_meta):
    set_metadata("0 * * * *", "retries", 3, path=tmp_meta)
    set_metadata("0 * * * *", "active", True, path=tmp_meta)
    assert get_metadata("0 * * * *", "retries", path=tmp_meta) == 3
    assert get_metadata("0 * * * *", "active", path=tmp_meta) is True
