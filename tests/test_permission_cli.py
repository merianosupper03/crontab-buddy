"""Tests for crontab_buddy.permission_cli."""
from __future__ import annotations

import pytest

from crontab_buddy import permission as perm_mod
from crontab_buddy import permission_cli as cli


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture(autouse=True)
def tp(tmp_path, monkeypatch):
    monkeypatch.setattr(perm_mod, "_PERMISSIONS_FILE", tmp_path / "permissions.json")


EXPR = "0 9 * * 1"


def test_cmd_set_prints(capsys):
    cli.cmd_permission_set(Args(expression=EXPR, user="alice", role="editor"))
    out = capsys.readouterr().out
    assert "Permission set" in out
    assert "alice" in out
    assert "editor" in out


def test_cmd_set_invalid_role_prints_error(capsys):
    cli.cmd_permission_set(Args(expression=EXPR, user="alice", role="god"))
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_get_existing(capsys):
    perm_mod.set_permission(EXPR, "bob", "viewer")
    cli.cmd_permission_get(Args(expression=EXPR, user="bob"))
    out = capsys.readouterr().out
    assert "viewer" in out


def test_cmd_get_missing(capsys):
    cli.cmd_permission_get(Args(expression=EXPR, user="ghost"))
    out = capsys.readouterr().out
    assert "No permission found" in out


def test_cmd_delete_success(capsys):
    perm_mod.set_permission(EXPR, "alice", "owner")
    cli.cmd_permission_delete(Args(expression=EXPR, user="alice"))
    out = capsys.readouterr().out
    assert "removed" in out.lower()


def test_cmd_delete_missing(capsys):
    cli.cmd_permission_delete(Args(expression=EXPR, user="nobody"))
    out = capsys.readouterr().out
    assert "No permission found" in out


def test_cmd_list_with_permissions(capsys):
    perm_mod.set_permission(EXPR, "alice", "owner")
    perm_mod.set_permission(EXPR, "bob", "viewer")
    cli.cmd_permission_list(Args(expression=EXPR))
    out = capsys.readouterr().out
    assert "alice" in out
    assert "bob" in out


def test_cmd_list_empty(capsys):
    cli.cmd_permission_list(Args(expression=EXPR))
    out = capsys.readouterr().out
    assert "No permissions" in out


def test_cmd_by_role_prints_matches(capsys):
    perm_mod.set_permission(EXPR, "alice", "editor")
    cli.cmd_permission_by_role(Args(role="editor"))
    out = capsys.readouterr().out
    assert "alice" in out


def test_cmd_by_role_invalid(capsys):
    cli.cmd_permission_by_role(Args(role="superadmin"))
    out = capsys.readouterr().out
    assert "Error" in out
