"""Tests for crontab_buddy.annotation."""

import pytest
from pathlib import Path
from crontab_buddy.annotation import (
    add_annotation,
    get_annotations,
    delete_annotation,
    clear_annotations,
    list_all_annotations,
)


@pytest.fixture
def tmp_ann(tmp_path):
    return tmp_path / "annotations.json"


def test_add_and_get(tmp_ann):
    add_annotation("* * * * *", "runs every minute", path=tmp_ann)
    entries = get_annotations("* * * * *", path=tmp_ann)
    assert len(entries) == 1
    assert entries[0]["text"] == "runs every minute"


def test_get_missing_returns_empty(tmp_ann):
    result = get_annotations("0 9 * * 1", path=tmp_ann)
    assert result == []


def test_add_with_author(tmp_ann):
    entry = add_annotation("0 0 * * *", "midnight job", author="alice", path=tmp_ann)
    assert entry["author"] == "alice"
    entries = get_annotations("0 0 * * *", path=tmp_ann)
    assert entries[0]["author"] == "alice"


def test_multiple_annotations_same_expression(tmp_ann):
    add_annotation("5 4 * * *", "first note", path=tmp_ann)
    add_annotation("5 4 * * *", "second note", path=tmp_ann)
    entries = get_annotations("5 4 * * *", path=tmp_ann)
    assert len(entries) == 2


def test_delete_existing(tmp_ann):
    add_annotation("0 12 * * *", "noon job", path=tmp_ann)
    result = delete_annotation("0 12 * * *", 0, path=tmp_ann)
    assert result is True
    assert get_annotations("0 12 * * *", path=tmp_ann) == []


def test_delete_missing_returns_false(tmp_ann):
    result = delete_annotation("0 6 * * *", 0, path=tmp_ann)
    assert result is False


def test_delete_out_of_range_returns_false(tmp_ann):
    add_annotation("0 6 * * *", "morning", path=tmp_ann)
    result = delete_annotation("0 6 * * *", 5, path=tmp_ann)
    assert result is False


def test_delete_removes_key_when_empty(tmp_ann):
    add_annotation("0 1 * * *", "only note", path=tmp_ann)
    delete_annotation("0 1 * * *", 0, path=tmp_ann)
    all_data = list_all_annotations(path=tmp_ann)
    assert "0 1 * * *" not in all_data


def test_clear_annotations(tmp_ann):
    add_annotation("*/5 * * * *", "note a", path=tmp_ann)
    add_annotation("*/5 * * * *", "note b", path=tmp_ann)
    count = clear_annotations("*/5 * * * *", path=tmp_ann)
    assert count == 2
    assert get_annotations("*/5 * * * *", path=tmp_ann) == []


def test_clear_missing_returns_zero(tmp_ann):
    count = clear_annotations("1 2 3 4 5", path=tmp_ann)
    assert count == 0


def test_empty_text_raises(tmp_ann):
    with pytest.raises(ValueError):
        add_annotation("* * * * *", "   ", path=tmp_ann)


def test_list_all_annotations(tmp_ann):
    add_annotation("0 9 * * 1", "mondays", path=tmp_ann)
    add_annotation("0 17 * * 5", "fridays", path=tmp_ann)
    all_data = list_all_annotations(path=tmp_ann)
    assert len(all_data) == 2
    assert "0 9 * * 1" in all_data
