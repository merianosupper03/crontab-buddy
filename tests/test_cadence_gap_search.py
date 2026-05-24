"""Tests for cadence_gap_search module."""

import json
import pytest
from unittest.mock import patch

from crontab_buddy.cadence_gap_search import (
    search_history_with_gaps,
    search_favorites_with_gaps,
    search_all_with_gaps,
)


FAKE_HISTORY = [
    {"expression": "0 9 * * *", "timestamp": "2024-01-01T09:00:00"},
    {"expression": "* * * * *", "timestamp": "2024-01-01T10:00:00"},
    {"expression": "0 9 * * *", "timestamp": "2024-01-01T11:00:00"},  # duplicate
]

FAKE_FAVORITES = {
    "daily_9am": "0 9 * * *",
    "every_minute": "* * * * *",
}


def test_search_history_returns_list():
    with patch("crontab_buddy.cadence_gap_search.get_history", return_value=FAKE_HISTORY):
        results = search_history_with_gaps(min_gap_hours=1)
    assert isinstance(results, list)


def test_search_history_daily_has_gaps():
    with patch("crontab_buddy.cadence_gap_search.get_history", return_value=FAKE_HISTORY):
        results = search_history_with_gaps(min_gap_hours=1)
    expressions = [r["expression"] for r in results]
    assert "0 9 * * *" in expressions


def test_search_history_every_minute_no_gaps():
    with patch("crontab_buddy.cadence_gap_search.get_history", return_value=FAKE_HISTORY):
        results = search_history_with_gaps(min_gap_hours=1)
    expressions = [r["expression"] for r in results]
    assert "* * * * *" not in expressions


def test_search_history_deduplicates():
    with patch("crontab_buddy.cadence_gap_search.get_history", return_value=FAKE_HISTORY):
        results = search_history_with_gaps(min_gap_hours=1)
    expressions = [r["expression"] for r in results]
    assert expressions.count("0 9 * * *") == 1


def test_search_history_result_has_required_keys():
    with patch("crontab_buddy.cadence_gap_search.get_history", return_value=FAKE_HISTORY):
        results = search_history_with_gaps(min_gap_hours=1)
    if results:
        keys = results[0].keys()
        assert "expression" in keys
        assert "gap_hours" in keys
        assert "gap_count" in keys
        assert "source" in keys


def test_search_history_source_label():
    with patch("crontab_buddy.cadence_gap_search.get_history", return_value=FAKE_HISTORY):
        results = search_history_with_gaps(min_gap_hours=1)
    for r in results:
        assert r["source"] == "history"


def test_search_favorites_returns_list():
    with patch("crontab_buddy.cadence_gap_search.list_favorites", return_value=FAKE_FAVORITES):
        results = search_favorites_with_gaps(min_gap_hours=1)
    assert isinstance(results, list)


def test_search_favorites_daily_has_gaps():
    with patch("crontab_buddy.cadence_gap_search.list_favorites", return_value=FAKE_FAVORITES):
        results = search_favorites_with_gaps(min_gap_hours=1)
    expressions = [r["expression"] for r in results]
    assert "0 9 * * *" in expressions


def test_search_favorites_source_label():
    with patch("crontab_buddy.cadence_gap_search.list_favorites", return_value=FAKE_FAVORITES):
        results = search_favorites_with_gaps(min_gap_hours=1)
    for r in results:
        assert r["source"] == "favorites"


def test_search_all_combines_sources():
    with patch("crontab_buddy.cadence_gap_search.get_history", return_value=FAKE_HISTORY), \
         patch("crontab_buddy.cadence_gap_search.list_favorites", return_value=FAKE_FAVORITES):
        results = search_all_with_gaps(min_gap_hours=1)
    assert isinstance(results, list)


def test_search_all_no_duplicate_expressions():
    with patch("crontab_buddy.cadence_gap_search.get_history", return_value=FAKE_HISTORY), \
         patch("crontab_buddy.cadence_gap_search.list_favorites", return_value=FAKE_FAVORITES):
        results = search_all_with_gaps(min_gap_hours=1)
    expressions = [r["expression"] for r in results]
    assert len(expressions) == len(set(expressions))
