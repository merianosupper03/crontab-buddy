"""Tests for crontab_buddy.versioning."""

import pytest

from crontab_buddy.versioning import (
    save_version,
    get_versions,
    get_version,
    delete_version,
    list_all_versions,
)

EXPR = "0 9 * * 1"


@pytest.fixture()
def tmp_ver(tmp_path):
    return str(tmp_path / "versions.json")


def test_save_and_get_version(tmp_ver):
    save_version(EXPR, "v1", note="initial", path=tmp_ver)
    entry = get_version(EXPR, "v1", path=tmp_ver)
    assert entry is not None
    assert entry["version"] == "v1"
    assert entry["note"] == "initial"


def test_get_missing_version_returns_none(tmp_ver):
    assert get_version(EXPR, "v99", path=tmp_ver) is None


def test_get_versions_returns_list(tmp_ver):
    save_version(EXPR, "v1", path=tmp_ver)
    save_version(EXPR, "v2", path=tmp_ver)
    versions = get_versions(EXPR, path=tmp_ver)
    assert len(versions) == 2
    assert versions[0]["version"] == "v1"
    assert versions[1]["version"] == "v2"


def test_overwrite_version_replaces_entry(tmp_ver):
    save_version(EXPR, "v1", note="old", path=tmp_ver)
    save_version(EXPR, "v1", note="new", path=tmp_ver)
    versions = get_versions(EXPR, path=tmp_ver)
    assert len(versions) == 1
    assert versions[0]["note"] == "new"


def test_delete_existing_version(tmp_ver):
    save_version(EXPR, "v1", path=tmp_ver)
    result = delete_version(EXPR, "v1", path=tmp_ver)
    assert result is True
    assert get_version(EXPR, "v1", path=tmp_ver) is None


def test_delete_missing_version_returns_false(tmp_ver):
    result = delete_version(EXPR, "ghost", path=tmp_ver)
    assert result is False


def test_saved_at_is_stored(tmp_ver):
    save_version(EXPR, "v1", path=tmp_ver)
    entry = get_version(EXPR, "v1", path=tmp_ver)
    assert "saved_at" in entry
    assert entry["saved_at"].endswith("+00:00")


def test_list_all_versions_multiple_expressions(tmp_ver):
    expr2 = "*/5 * * * *"
    save_version(EXPR, "v1", path=tmp_ver)
    save_version(expr2, "v1", path=tmp_ver)
    all_v = list_all_versions(path=tmp_ver)
    assert EXPR in all_v
    assert expr2 in all_v


def test_get_versions_empty_for_unknown_expression(tmp_ver):
    assert get_versions("9 9 9 9 9", path=tmp_ver) == []


def test_expression_stripped_before_storing(tmp_ver):
    save_version("  " + EXPR + "  ", "v1", path=tmp_ver)
    assert get_version(EXPR, "v1", path=tmp_ver) is not None
