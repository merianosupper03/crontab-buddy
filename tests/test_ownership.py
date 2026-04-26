"""Tests for crontab_buddy.ownership."""

import pytest

from crontab_buddy.ownership import (
    delete_owner,
    find_by_owner,
    find_by_team,
    get_owner,
    list_owners,
    set_owner,
)

EXPR = "0 9 * * 1"
EXPR2 = "*/5 * * * *"


@pytest.fixture
def tmp_own(tmp_path):
    return str(tmp_path / "ownership.json")


def test_set_and_get(tmp_own):
    set_owner(EXPR, "alice", path=tmp_own)
    record = get_owner(EXPR, path=tmp_own)
    assert record is not None
    assert record["owner"] == "alice"


def test_get_missing_returns_none(tmp_own):
    assert get_owner(EXPR, path=tmp_own) is None


def test_set_with_team_and_email(tmp_own):
    set_owner(EXPR, "bob", team="ops", email="bob@example.com", path=tmp_own)
    record = get_owner(EXPR, path=tmp_own)
    assert record["team"] == "ops"
    assert record["email"] == "bob@example.com"


def test_overwrite_owner(tmp_own):
    set_owner(EXPR, "alice", path=tmp_own)
    set_owner(EXPR, "carol", path=tmp_own)
    assert get_owner(EXPR, path=tmp_own)["owner"] == "carol"


def test_delete_existing(tmp_own):
    set_owner(EXPR, "alice", path=tmp_own)
    assert delete_owner(EXPR, path=tmp_own) is True
    assert get_owner(EXPR, path=tmp_own) is None


def test_delete_missing_returns_false(tmp_own):
    assert delete_owner(EXPR, path=tmp_own) is False


def test_list_owners_empty(tmp_own):
    assert list_owners(path=tmp_own) == []


def test_list_owners_multiple(tmp_own):
    set_owner(EXPR, "alice", path=tmp_own)
    set_owner(EXPR2, "bob", path=tmp_own)
    records = list_owners(path=tmp_own)
    assert len(records) == 2
    exprs = {r["expression"] for r in records}
    assert EXPR in exprs
    assert EXPR2 in exprs


def test_find_by_owner_match(tmp_own):
    set_owner(EXPR, "alice", path=tmp_own)
    set_owner(EXPR2, "bob", path=tmp_own)
    results = find_by_owner("alice", path=tmp_own)
    assert len(results) == 1
    assert results[0]["expression"] == EXPR


def test_find_by_owner_case_insensitive(tmp_own):
    set_owner(EXPR, "Alice", path=tmp_own)
    results = find_by_owner("alice", path=tmp_own)
    assert len(results) == 1


def test_find_by_owner_no_match(tmp_own):
    set_owner(EXPR, "alice", path=tmp_own)
    assert find_by_owner("dave", path=tmp_own) == []


def test_find_by_team(tmp_own):
    set_owner(EXPR, "alice", team="ops", path=tmp_own)
    set_owner(EXPR2, "bob", team="dev", path=tmp_own)
    results = find_by_team("ops", path=tmp_own)
    assert len(results) == 1
    assert results[0]["expression"] == EXPR


def test_find_by_team_case_insensitive(tmp_own):
    set_owner(EXPR, "alice", team="OPS", path=tmp_own)
    results = find_by_team("ops", path=tmp_own)
    assert len(results) == 1
