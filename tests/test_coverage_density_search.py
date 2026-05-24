"""Tests for coverage_density_search module."""

import pytest
from unittest.mock import patch

from crontab_buddy.coverage_density_search import (
    search_history_by_coverage_density,
    search_favorites_by_coverage_density,
)


FAKE_HISTORY = ["* * * * *", "0 9 * * *", "0 * * * *", "bad expr"]
FAKE_FAVORITES = {
    "every_minute": "* * * * *",
    "daily_9am": "0 9 * * *",
    "broken": "bad expr",
}


@patch("crontab_buddy.coverage_density_search.get_history", return_value=FAKE_HISTORY)
def test_search_history_returns_list(mock_hist):
    results = search_history_by_coverage_density()
    assert isinstance(results, list)


@patch("crontab_buddy.coverage_density_search.get_history", return_value=FAKE_HISTORY)
def test_search_history_excludes_invalid(mock_hist):
    results = search_history_by_coverage_density()
    exprs = [r["expression"] for r in results]
    assert "bad expr" not in exprs


@patch("crontab_buddy.coverage_density_search.get_history", return_value=FAKE_HISTORY)
def test_search_history_result_has_required_keys(mock_hist):
    results = search_history_by_coverage_density()
    assert len(results) > 0
    for r in results:
        assert "expression" in r
        assert "score" in r
        assert "grade" in r
        assert "source" in r
        assert r["source"] == "history"


@patch("crontab_buddy.coverage_density_search.get_history", return_value=FAKE_HISTORY)
def test_search_history_min_score_filters(mock_hist):
    all_results = search_history_by_coverage_density(min_score=0.0)
    high_results = search_history_by_coverage_density(min_score=0.9)
    assert len(high_results) <= len(all_results)
    for r in high_results:
        assert r["score"] >= 0.9


@patch("crontab_buddy.coverage_density_search.get_history", return_value=FAKE_HISTORY)
def test_search_history_no_duplicates(mock_hist):
    results = search_history_by_coverage_density()
    exprs = [r["expression"] for r in results]
    assert len(exprs) == len(set(exprs))


@patch("crontab_buddy.coverage_density_search.list_favorites", return_value=FAKE_FAVORITES)
def test_search_favorites_returns_list(mock_fav):
    results = search_favorites_by_coverage_density()
    assert isinstance(results, list)


@patch("crontab_buddy.coverage_density_search.list_favorites", return_value=FAKE_FAVORITES)
def test_search_favorites_excludes_invalid(mock_fav):
    results = search_favorites_by_coverage_density()
    exprs = [r["expression"] for r in results]
    assert "bad expr" not in exprs


@patch("crontab_buddy.coverage_density_search.list_favorites", return_value=FAKE_FAVORITES)
def test_search_favorites_result_has_name(mock_fav):
    results = search_favorites_by_coverage_density()
    assert len(results) > 0
    for r in results:
        assert "name" in r
        assert "expression" in r
        assert r["source"] == "favorites"


@patch("crontab_buddy.coverage_density_search.list_favorites", return_value=FAKE_FAVORITES)
def test_search_favorites_grade_filter(mock_fav):
    all_results = search_favorites_by_coverage_density()
    if all_results:
        target_grade = all_results[0]["grade"]
        filtered = search_favorites_by_coverage_density(grade=target_grade)
        for r in filtered:
            assert r["grade"].lower() == target_grade.lower()
