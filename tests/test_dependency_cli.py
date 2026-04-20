"""Tests for crontab_buddy.dependency_cli."""
import pytest

from crontab_buddy.dependency import add_dependency
from crontab_buddy.dependency_cli import (
    cmd_dep_add,
    cmd_dep_clear,
    cmd_dep_list,
    cmd_dep_list_all,
    cmd_dep_remove,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture()
def tp(tmp_path, monkeypatch):
    dep_path = tmp_path / "deps.json"
    import crontab_buddy.dependency as dep_mod
    monkeypatch.setattr(dep_mod, "_DEFAULT_PATH", dep_path)
    import crontab_buddy.dependency_cli  # noqa: F401 — reload not needed, functions call module-level
    return dep_path


def test_cmd_dep_add_prints_added(tp, capsys):
    cmd_dep_add(Args(schedule="nightly", depends_on="backup"))
    out = capsys.readouterr().out
    assert "added" in out.lower()
    assert "nightly" in out


def test_cmd_dep_add_duplicate_message(tp, capsys):
    cmd_dep_add(Args(schedule="nightly", depends_on="backup"))
    cmd_dep_add(Args(schedule="nightly", depends_on="backup"))
    out = capsys.readouterr().out
    assert "already" in out.lower()


def test_cmd_dep_remove_success(tp, capsys):
    add_dependency("nightly", "backup", tp)
    cmd_dep_remove(Args(schedule="nightly", depends_on="backup"))
    out = capsys.readouterr().out
    assert "removed" in out.lower()


def test_cmd_dep_remove_missing(tp, capsys):
    cmd_dep_remove(Args(schedule="nightly", depends_on="ghost"))
    out = capsys.readouterr().out
    assert "no such" in out.lower()


def test_cmd_dep_list_with_deps(tp, capsys):
    add_dependency("nightly", "backup", tp)
    add_dependency("nightly", "cleanup", tp)
    cmd_dep_list(Args(schedule="nightly"))
    out = capsys.readouterr().out
    assert "backup" in out
    assert "cleanup" in out


def test_cmd_dep_list_no_deps(tp, capsys):
    cmd_dep_list(Args(schedule="nightly"))
    out = capsys.readouterr().out
    assert "no dependencies" in out.lower()


def test_cmd_dep_list_all_prints_all(tp, capsys):
    add_dependency("a", "b", tp)
    add_dependency("x", "y", tp)
    cmd_dep_list_all(Args())
    out = capsys.readouterr().out
    assert "a" in out
    assert "x" in out


def test_cmd_dep_list_all_empty(tp, capsys):
    cmd_dep_list_all(Args())
    out = capsys.readouterr().out
    assert "no dependencies" in out.lower()


def test_cmd_dep_clear_prints(tp, capsys):
    add_dependency("nightly", "backup", tp)
    cmd_dep_clear(Args(schedule="nightly"))
    out = capsys.readouterr().out
    assert "cleared" in out.lower()
