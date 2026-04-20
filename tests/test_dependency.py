"""Tests for crontab_buddy.dependency."""
import pytest

from crontab_buddy.dependency import (
    add_dependency,
    clear_dependencies,
    get_dependencies,
    list_all_dependencies,
    remove_dependency,
)


@pytest.fixture()
def tmp_dep(tmp_path):
    return tmp_path / "deps.json"


def test_add_and_get(tmp_dep):
    add_dependency("nightly", "backup", tmp_dep)
    deps = get_dependencies("nightly", tmp_dep)
    assert "backup" in deps


def test_add_duplicate_returns_false(tmp_dep):
    add_dependency("nightly", "backup", tmp_dep)
    result = add_dependency("nightly", "backup", tmp_dep)
    assert result is False


def test_add_duplicate_not_duplicated_in_list(tmp_dep):
    add_dependency("nightly", "backup", tmp_dep)
    add_dependency("nightly", "backup", tmp_dep)
    assert get_dependencies("nightly", tmp_dep).count("backup") == 1


def test_add_multiple_dependencies(tmp_dep):
    add_dependency("nightly", "backup", tmp_dep)
    add_dependency("nightly", "cleanup", tmp_dep)
    deps = get_dependencies("nightly", tmp_dep)
    assert "backup" in deps
    assert "cleanup" in deps


def test_remove_existing(tmp_dep):
    add_dependency("nightly", "backup", tmp_dep)
    result = remove_dependency("nightly", "backup", tmp_dep)
    assert result is True
    assert get_dependencies("nightly", tmp_dep) == []


def test_remove_missing_returns_false(tmp_dep):
    result = remove_dependency("nightly", "ghost", tmp_dep)
    assert result is False


def test_case_insensitive_keys(tmp_dep):
    add_dependency("Nightly", "Backup", tmp_dep)
    deps = get_dependencies("nightly", tmp_dep)
    assert "backup" in deps


def test_get_missing_schedule_returns_empty(tmp_dep):
    assert get_dependencies("nonexistent", tmp_dep) == []


def test_list_all_returns_all(tmp_dep):
    add_dependency("a", "b", tmp_dep)
    add_dependency("a", "c", tmp_dep)
    add_dependency("x", "y", tmp_dep)
    all_deps = list_all_dependencies(tmp_dep)
    assert "a" in all_deps
    assert "x" in all_deps
    assert len(all_deps["a"]) == 2


def test_clear_dependencies(tmp_dep):
    add_dependency("nightly", "backup", tmp_dep)
    clear_dependencies("nightly", tmp_dep)
    assert get_dependencies("nightly", tmp_dep) == []


def test_clear_nonexistent_schedule_no_error(tmp_dep):
    clear_dependencies("ghost", tmp_dep)  # should not raise
