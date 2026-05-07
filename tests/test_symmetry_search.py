import pytest
from unittest.mock import patch
from crontab_buddy.symmetry_search import (
    find_symmetric_in_history,
    find_symmetric_in_favorites,
)


FAKE_HISTORY = [
    {"expression": "0 9 * * 1"},
    {"expression": "0 9 * * 2"},
    {"expression": "30 22 * * *"},
    {"expression": "0 9 * * 1"},  # duplicate — should be skipped
]

FAKE_FAVORITES = [
    ("weekday-morning", "0 9 * * 1"),
    ("late-night", "30 22 * * *"),
    ("same", "0 9 * * *"),
]


@patch("crontab_buddy.symmetry_search.get_history", return_value=FAKE_HISTORY)
def test_find_symmetric_in_history_returns_list(mock_hist):
    results = find_symmetric_in_history("0 9 * * *", min_score=0.0)
    assert isinstance(results, list)


@patch("crontab_buddy.symmetry_search.get_history", return_value=FAKE_HISTORY)
def test_find_symmetric_in_history_excludes_self(mock_hist):
    results = find_symmetric_in_history("0 9 * * 1", min_score=0.0)
    for r in results:
        assert r["expression"] != "0 9 * * 1"


@patch("crontab_buddy.symmetry_search.get_history", return_value=FAKE_HISTORY)
def test_find_symmetric_in_history_no_duplicates(mock_hist):
    results = find_symmetric_in_history("0 9 * * *", min_score=0.0)
    expressions = [r["expression"] for r in results]
    assert len(expressions) == len(set(expressions))


@patch("crontab_buddy.symmetry_search.get_history", return_value=FAKE_HISTORY)
def test_find_symmetric_in_history_sorted_by_score(mock_hist):
    results = find_symmetric_in_history("0 9 * * *", min_score=0.0)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


@patch("crontab_buddy.symmetry_search.get_history", return_value=FAKE_HISTORY)
def test_find_symmetric_in_history_result_has_keys(mock_hist):
    results = find_symmetric_in_history("0 9 * * *", min_score=0.0)
    for r in results:
        assert "expression" in r
        assert "score" in r
        assert "label" in r


@patch("crontab_buddy.symmetry_search.list_favorites", return_value=FAKE_FAVORITES)
def test_find_symmetric_in_favorites_returns_list(mock_fav):
    results = find_symmetric_in_favorites("0 9 * * *", min_score=0.0)
    assert isinstance(results, list)


@patch("crontab_buddy.symmetry_search.list_favorites", return_value=FAKE_FAVORITES)
def test_find_symmetric_in_favorites_excludes_self(mock_fav):
    results = find_symmetric_in_favorites("0 9 * * *", min_score=0.0)
    for r in results:
        assert r["expression"] != "0 9 * * *"


@patch("crontab_buddy.symmetry_search.list_favorites", return_value=FAKE_FAVORITES)
def test_find_symmetric_in_favorites_has_name_key(mock_fav):
    results = find_symmetric_in_favorites("0 9 * * *", min_score=0.0)
    for r in results:
        assert "name" in r


@patch("crontab_buddy.symmetry_search.list_favorites", return_value=FAKE_FAVORITES)
def test_find_symmetric_in_favorites_min_score_filters(mock_fav):
    results = find_symmetric_in_favorites("0 9 * * *", min_score=0.99)
    for r in results:
        assert r["score"] >= 0.99
