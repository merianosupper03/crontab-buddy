"""Tests for crontab_buddy.history."""

import json
import pytest
from pathlib import Path
from crontab_buddy.history import (
    add_entry, get_history, clear_history, search_history, MAX_HISTORY
)


@pytest.fixture
def tmp_hist(tmp_path):
    return tmp_path / "history.json"


def test_add_and_retrieve(tmp_hist):
    add_entry("0 * * * *", "hourly", path=tmp_hist)
    entries = get_history(path=tmp_hist)
    assert len(entries) == 1
    assert entries[0]["expression"] == "0 * * * *"
    assert entries[0]["comment"] == "hourly"


def test_no_consecutive_duplicate(tmp_hist):
    add_entry("0 * * * *", path=tmp_hist)
    add_entry("0 * * * *", path=tmp_hist)
    assert len(get_history(path=tmp_hist)) == 1


def test_different_entries_both_stored(tmp_hist):
    add_entry("0 * * * *", path=tmp_hist)
    add_entry("*/5 * * * *", path=tmp_hist)
    assert len(get_history(path=tmp_hist)) == 2


def test_clear_history(tmp_hist):
    add_entry("0 * * * *", path=tmp_hist)
    clear_history(path=tmp_hist)
    assert get_history(path=tmp_hist) == []
    assert not tmp_hist.exists()


def test_clear_nonexistent_history(tmp_hist):
    clear_history(path=tmp_hist)  # should not raise


def test_max_history_trimmed(tmp_hist):
    for i in range(MAX_HISTORY + 10):
        add_entry(f"{i} * * * *", path=tmp_hist)
    entries = get_history(path=tmp_hist)
    assert len(entries) == MAX_HISTORY


def test_search_by_expression(tmp_hist):
    add_entry("0 9 * * 1", "weekly meeting", path=tmp_hist)
    add_entry("*/5 * * * *", "poll", path=tmp_hist)
    results = search_history("weekly", path=tmp_hist)
    assert len(results) == 1
    assert results[0]["expression"] == "0 9 * * 1"


def test_search_case_insensitive(tmp_hist):
    add_entry("0 0 * * *", "Daily Backup", path=tmp_hist)
    results = search_history("daily", path=tmp_hist)
    assert len(results) == 1


def test_search_no_match(tmp_hist):
    add_entry("0 0 * * *", "backup", path=tmp_hist)
    assert search_history("deploy", path=tmp_hist) == []


def test_empty_history_file_missing(tmp_hist):
    assert get_history(path=tmp_hist) == []


def test_corrupted_history_returns_empty(tmp_hist):
    tmp_hist.write_text("not json")
    assert get_history(path=tmp_hist) == []
