"""Tests for crontab_buddy.coverage_gap_search."""

import json
import pytest
from unittest.mock import patch

from crontab_buddy.coverage_gap_search import (
    search_history_with_gaps,
    search_favorites_with_gaps,
    search_all_with_gaps,
)


_HISTORY_DAILY = [
    {"expression": "0 9 * * *"},   # fires only at hour 9 — 23 gaps
    {"expression": "* * * * *"},   # fires every minute — 0 gaps
]

_FAVORITES = {
    "midnight": "0 0 * * *",
    "every_minute": "* * * * *",
}


def test_search_history_returns_list():
    with patch("crontab_buddy.coverage_gap_search.get_history", return_value=_HISTORY_DAILY):
        results = search_history_with_gaps(min_gap_hours=1)
    assert isinstance(results, list)


def test_search_history_daily_has_gaps():
    with patch("crontab_buddy.coverage_gap_search.get_history", return_value=_HISTORY_DAILY):
        results = search_history_with_gaps(min_gap_hours=1)
    exprs = [r["expression"] for r in results]
    assert "0 9 * * *" in exprs


def test_search_history_every_minute_excluded():
    with patch("crontab_buddy.coverage_gap_search.get_history", return_value=_HISTORY_DAILY):
        results = search_history_with_gaps(min_gap_hours=1)
    exprs = [r["expression"] for r in results]
    assert "* * * * *" not in exprs


def test_search_history_result_has_required_keys():
    with patch("crontab_buddy.coverage_gap_search.get_history", return_value=_HISTORY_DAILY):
        results = search_history_with_gaps(min_gap_hours=1)
    assert results
    for r in results:
        assert "expression" in r
        assert "gap_hours" in r
        assert "gap_count" in r
        assert "source" in r


def test_search_history_source_is_history():
    with patch("crontab_buddy.coverage_gap_search.get_history", return_value=_HISTORY_DAILY):
        results = search_history_with_gaps(min_gap_hours=1)
    for r in results:
        assert r["source"] == "history"


def test_search_history_deduplicates():
    duped = _HISTORY_DAILY + [{"expression": "0 9 * * *"}]
    with patch("crontab_buddy.coverage_gap_search.get_history", return_value=duped):
        results = search_history_with_gaps(min_gap_hours=1)
    exprs = [r["expression"] for r in results]
    assert exprs.count("0 9 * * *") == 1


def test_search_favorites_returns_list():
    with patch("crontab_buddy.coverage_gap_search.list_favorites", return_value=_FAVORITES):
        results = search_favorites_with_gaps(min_gap_hours=1)
    assert isinstance(results, list)


def test_search_favorites_midnight_has_gaps():
    with patch("crontab_buddy.coverage_gap_search.list_favorites", return_value=_FAVORITES):
        results = search_favorites_with_gaps(min_gap_hours=1)
    exprs = [r["expression"] for r in results]
    assert "0 0 * * *" in exprs


def test_search_favorites_source_is_favorites():
    with patch("crontab_buddy.coverage_gap_search.list_favorites", return_value=_FAVORITES):
        results = search_favorites_with_gaps(min_gap_hours=1)
    for r in results:
        assert r["source"] == "favorites"


def test_search_all_combines_sources():
    with patch("crontab_buddy.coverage_gap_search.get_history", return_value=_HISTORY_DAILY), \
         patch("crontab_buddy.coverage_gap_search.list_favorites", return_value=_FAVORITES):
        results = search_all_with_gaps(min_gap_hours=1)
    sources = {r["source"] for r in results}
    assert "history" in sources
    assert "favorites" in sources


def test_search_all_respects_max_results():
    history = [{"expression": f"0 {h} * * *"} for h in range(10)]
    with patch("crontab_buddy.coverage_gap_search.get_history", return_value=history), \
         patch("crontab_buddy.coverage_gap_search.list_favorites", return_value={}):
        results = search_all_with_gaps(min_gap_hours=1, max_results=3)
    assert len(results) <= 3
