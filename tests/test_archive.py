import pytest
import json
from crontab_buddy.archive import (
    archive_expression, get_archive, delete_from_archive,
    clear_archive, search_archive
)


@pytest.fixture
def tmp_archive(tmp_path):
    return str(tmp_path / "archive.json")


def test_archive_and_retrieve(tmp_archive):
    archive_expression("0 5 * * *", reason="old", path=tmp_archive)
    entries = get_archive(path=tmp_archive)
    assert len(entries) == 1
    assert entries[0]["expression"] == "0 5 * * *"
    assert entries[0]["reason"] == "old"


def test_archive_no_reason(tmp_archive):
    archive_expression("*/5 * * * *", path=tmp_archive)
    entries = get_archive(path=tmp_archive)
    assert entries[0]["reason"] == ""


def test_archive_multiple(tmp_archive):
    archive_expression("0 1 * * *", path=tmp_archive)
    archive_expression("0 2 * * *", path=tmp_archive)
    assert len(get_archive(path=tmp_archive)) == 2


def test_archive_has_timestamp(tmp_archive):
    entry = archive_expression("* * * * *", path=tmp_archive)
    assert "archived_at" in entry
    assert "T" in entry["archived_at"]


def test_delete_existing(tmp_archive):
    archive_expression("0 5 * * *", path=tmp_archive)
    result = delete_from_archive("0 5 * * *", path=tmp_archive)
    assert result is True
    assert get_archive(path=tmp_archive) == []


def test_delete_missing_returns_false(tmp_archive):
    result = delete_from_archive("0 5 * * *", path=tmp_archive)
    assert result is False


def test_delete_only_removes_matching(tmp_archive):
    """Deleting one expression should leave other entries intact."""
    archive_expression("0 5 * * *", path=tmp_archive)
    archive_expression("0 6 * * *", path=tmp_archive)
    delete_from_archive("0 5 * * *", path=tmp_archive)
    entries = get_archive(path=tmp_archive)
    assert len(entries) == 1
    assert entries[0]["expression"] == "0 6 * * *"


def test_clear_archive(tmp_archive):
    archive_expression("* * * * *", path=tmp_archive)
    clear_archive(path=tmp_archive)
    assert get_archive(path=tmp_archive) == []


def test_search_by_expression(tmp_archive):
    archive_expression("0 5 * * 1", reason="weekly", path=tmp_archive)
    archive_expression("*/15 * * * *", path=tmp_archive)
    results = search_archive("0 5", path=tmp_archive)
    assert len(results) == 1
    assert results[0]["expression"] == "0 5 * * 1"


def test_search_by_reason(tmp_archive):
    archive_expression("0 0 * * *", reason="deprecated job", path=tmp_archive)
    results = search_archive("deprecated", path=tmp_archive)
    assert len(results) == 1


def test_search_no_match(tmp_archive):
    archive_expression("* * * * *", path=tmp_archive)
    assert search_archive("nonexistent", path=tmp_archive) == []
