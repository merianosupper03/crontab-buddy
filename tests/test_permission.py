"""Tests for crontab_buddy.permission."""
from __future__ import annotations

import pytest

from crontab_buddy import permission as perm_mod


@pytest.fixture(autouse=True)
def tmp_permissions(tmp_path, monkeypatch):
    monkeypatch.setattr(perm_mod, "_PERMISSIONS_FILE", tmp_path / "permissions.json")


EXPR = "0 9 * * 1"


def test_set_and_get():
    perm_mod.set_permission(EXPR, "alice", "editor")
    assert perm_mod.get_permission(EXPR, "alice") == "editor"


def test_get_missing_returns_none():
    assert perm_mod.get_permission(EXPR, "bob") is None


def test_overwrite_permission():
    perm_mod.set_permission(EXPR, "alice", "viewer")
    perm_mod.set_permission(EXPR, "alice", "owner")
    assert perm_mod.get_permission(EXPR, "alice") == "owner"


def test_invalid_role_raises():
    with pytest.raises(ValueError, match="Invalid role"):
        perm_mod.set_permission(EXPR, "alice", "superuser")


def test_all_valid_roles_accepted():
    for role in ("owner", "editor", "viewer"):
        perm_mod.set_permission(EXPR, f"user_{role}", role)
        assert perm_mod.get_permission(EXPR, f"user_{role}") == role


def test_delete_existing():
    perm_mod.set_permission(EXPR, "alice", "viewer")
    assert perm_mod.delete_permission(EXPR, "alice") is True
    assert perm_mod.get_permission(EXPR, "alice") is None


def test_delete_missing_returns_false():
    assert perm_mod.delete_permission(EXPR, "ghost") is False


def test_get_all_permissions():
    perm_mod.set_permission(EXPR, "alice", "owner")
    perm_mod.set_permission(EXPR, "bob", "viewer")
    perms = perm_mod.get_all_permissions(EXPR)
    assert perms == {"alice": "owner", "bob": "viewer"}


def test_get_all_permissions_missing_expression():
    assert perm_mod.get_all_permissions("* * * * *") == {}


def test_list_users_with_role():
    perm_mod.set_permission(EXPR, "alice", "editor")
    perm_mod.set_permission("*/5 * * * *", "bob", "editor")
    perm_mod.set_permission(EXPR, "carol", "viewer")
    results = perm_mod.list_users_with_role("editor")
    users = {r["user"] for r in results}
    assert "alice" in users
    assert "bob" in users
    assert "carol" not in users


def test_list_users_with_invalid_role_raises():
    with pytest.raises(ValueError):
        perm_mod.list_users_with_role("admin")


def test_delete_cleans_up_empty_expression():
    perm_mod.set_permission(EXPR, "alice", "viewer")
    perm_mod.delete_permission(EXPR, "alice")
    data = perm_mod._load()
    assert EXPR not in data
