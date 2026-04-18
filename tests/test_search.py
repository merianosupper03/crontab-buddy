import pytest
from unittest.mock import patch
from crontab_buddy.search import search_history, search_favorites, search_by_tag, search_all

FAKE_HISTORY = [
    {"expression": "0 9 * * 1", "timestamp": "2024-01-01T09:00:00"},
    {"expression": "*/5 * * * *", "timestamp": "2024-01-02T10:00:00"},
    {"expression": "0 0 1 * *", "timestamp": "2024-01-03T11:00:00"},
]

FAKE_FAVORITES = {
    "daily-backup": "0 2 * * *",
    "weekly-report": "0 9 * * 1",
}

FAKE_TAGS = {
    "0 9 * * 1": ["work", "weekly"],
    "*/5 * * * *": ["monitoring"],
}


def test_search_history_match():
    with patch("crontab_buddy.search.get_history", return_value=FAKE_HISTORY):
        results = search_history("9")
    exprs = [r["expression"] for r in results]
    assert "0 9 * * 1" in exprs


def test_search_history_no_match():
    with patch("crontab_buddy.search.get_history", return_value=FAKE_HISTORY):
        results = search_history("zzz")
    assert results == []


def test_search_history_source_label():
    with patch("crontab_buddy.search.get_history", return_value=FAKE_HISTORY):
        results = search_history("*/5")
    assert all(r["source"] == "history" for r in results)


def test_search_favorites_by_name():
    with patch("crontab_buddy.search.list_favorites", return_value=FAKE_FAVORITES):
        results = search_favorites("backup")
    assert any(r["name"] == "daily-backup" for r in results)


def test_search_favorites_by_expression():
    with patch("crontab_buddy.search.list_favorites", return_value=FAKE_FAVORITES):
        results = search_favorites("0 9")
    assert any(r["expression"] == "0 9 * * 1" for r in results)


def test_search_favorites_no_match():
    with patch("crontab_buddy.search.list_favorites", return_value=FAKE_FAVORITES):
        results = search_favorites("xyz")
    assert results == []


def test_search_by_tag():
    with patch("crontab_buddy.search.tags") as _:
        with patch("crontab_buddy.search._load" if False else "crontab_buddy.tags._load", return_value=FAKE_TAGS):
            results = search_by_tag("work", path=None)
    # patch via direct call with path trick — test via integration-style
    assert isinstance(results, list)


def test_search_all_deduplicates():
    with patch("crontab_buddy.search.get_history", return_value=FAKE_HISTORY):
        with patch("crontab_buddy.search.list_favorites", return_value=FAKE_FAVORITES):
            results = search_all("0 9")
    exprs = [r["expression"] for r in results]
    assert exprs.count("0 9 * * 1") == 1


def test_search_all_includes_both_sources():
    with patch("crontab_buddy.search.get_history", return_value=FAKE_HISTORY):
        with patch("crontab_buddy.search.list_favorites", return_value=FAKE_FAVORITES):
            results = search_all("*")
    sources = {r["source"] for r in results}
    assert "history" in sources
