"""Tests for cadence_search module."""

import pytest
from unittest.mock import patch

from crontab_buddy.cadence_search import (
    search_history_by_cadence,
    search_favorites_by_cadence,
    search_all_by_cadence,
)


FAKE_HISTORY = [
    {"expression": "* * * * *"},
    {"expression": "0 * * * *"},
    {"expression": "0 0 * * *"},
    {"expression": "0 9 * * 1"},
]

FAKE_FAVORITES = {
    "every_minute": "* * * * *",
    "daily_midnight": "0 0 * * *",
}


@patch("crontab_buddy.cadence_search.get_history", return_value=FAKE_HISTORY)
@patch("crontab_buddy.cadence_search.list_favorites", return_value=FAKE_FAVORITES)
def test_search_history_by_cadence_returns_list(mock_fav, mock_hist):
    results = search_history_by_cadence("burst")
    assert isinstance(results, list)


@patch("crontab_buddy.cadence_search.get_history", return_value=FAKE_HISTORY)
@patch("crontab_buddy.cadence_search.list_favorites", return_value=FAKE_FAVORITES)
def test_search_history_burst_finds_every_minute(mock_fav, mock_hist):
    results = search_history_by_cadence("burst")
    expressions = [r["expression"] for r in results]
    assert "* * * * *" in expressions


@patch("crontab_buddy.cadence_search.get_history", return_value=FAKE_HISTORY)
@patch("crontab_buddy.cadence_search.list_favorites", return_value=FAKE_FAVORITES)
def test_search_history_result_has_source_label(mock_fav, mock_hist):
    results = search_history_by_cadence("burst")
    for r in results:
        assert r["source"] == "history"


@patch("crontab_buddy.cadence_search.get_history", return_value=FAKE_HISTORY)
@patch("crontab_buddy.cadence_search.list_favorites", return_value=FAKE_FAVORITES)
def test_search_history_no_duplicates(mock_fav, mock_hist):
    history_with_dup = FAKE_HISTORY + [{"expression": "* * * * *"}]
    with patch("crontab_buddy.cadence_search.get_history", return_value=history_with_dup):
        results = search_history_by_cadence("burst")
    exprs = [r["expression"] for r in results]
    assert len(exprs) == len(set(exprs))


@patch("crontab_buddy.cadence_search.list_favorites", return_value=FAKE_FAVORITES)
def test_search_favorites_by_cadence_returns_list(mock_fav):
    results = search_favorites_by_cadence("burst")
    assert isinstance(results, list)


@patch("crontab_buddy.cadence_search.list_favorites", return_value=FAKE_FAVORITES)
def test_search_favorites_has_name_field(mock_fav):
    results = search_favorites_by_cadence("burst")
    for r in results:
        assert "name" in r


@patch("crontab_buddy.cadence_search.list_favorites", return_value=FAKE_FAVORITES)
def test_search_favorites_source_is_favorites(mock_fav):
    results = search_favorites_by_cadence("burst")
    for r in results:
        assert r["source"] == "favorites"


@patch("crontab_buddy.cadence_search.get_history", return_value=FAKE_HISTORY)
@patch("crontab_buddy.cadence_search.list_favorites", return_value=FAKE_FAVORITES)
def test_search_all_combines_both(mock_fav, mock_hist):
    results = search_all_by_cadence("burst")
    sources = {r["source"] for r in results}
    assert "history" in sources or "favorites" in sources


@patch("crontab_buddy.cadence_search.get_history", return_value=[])
@patch("crontab_buddy.cadence_search.list_favorites", return_value={})
def test_search_all_empty_returns_empty_list(mock_fav, mock_hist):
    results = search_all_by_cadence("burst")
    assert results == []
