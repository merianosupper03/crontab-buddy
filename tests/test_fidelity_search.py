"""Tests for fidelity_search and fidelity_search_cli."""

import json
import os
import pytest
from unittest.mock import patch

from crontab_buddy.fidelity_search import (
    search_history_by_fidelity,
    search_favorites_by_fidelity,
    search_above_score,
)
from crontab_buddy.fidelity_search_cli import (
    cmd_fidelity_search_history,
    cmd_fidelity_search_favorites,
    cmd_fidelity_search_all,
)


FAKE_HISTORY = [
    {"expression": "0 9 * * 1", "timestamp": "2024-01-01T09:00:00"},
    {"expression": "* * * * *", "timestamp": "2024-01-02T00:00:00"},
    {"expression": "bad expr", "timestamp": "2024-01-03T00:00:00"},
]

FAKE_FAVORITES = [
    ("daily-nine", "0 9 * * 1"),
    ("every-min", "* * * * *"),
]


class Args:
    def __init__(self, min_score=0.0):
        self.min_score = min_score


def test_search_history_returns_list():
    with patch("crontab_buddy.fidelity_search.get_history", return_value=FAKE_HISTORY):
        results = search_history_by_fidelity(0.0)
    assert isinstance(results, list)


def test_search_history_excludes_invalid():
    with patch("crontab_buddy.fidelity_search.get_history", return_value=FAKE_HISTORY):
        results = search_history_by_fidelity(0.0)
    expressions = [r["expression"] for r in results]
    assert "bad expr" not in expressions


def test_search_history_has_required_keys():
    with patch("crontab_buddy.fidelity_search.get_history", return_value=FAKE_HISTORY):
        results = search_history_by_fidelity(0.0)
    for r in results:
        assert "expression" in r
        assert "score" in r
        assert "grade" in r
        assert r["source"] == "history"


def test_search_history_sorted_by_score_desc():
    with patch("crontab_buddy.fidelity_search.get_history", return_value=FAKE_HISTORY):
        results = search_history_by_fidelity(0.0)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_search_history_no_duplicates():
    doubled = FAKE_HISTORY + FAKE_HISTORY
    with patch("crontab_buddy.fidelity_search.get_history", return_value=doubled):
        results = search_history_by_fidelity(0.0)
    expressions = [r["expression"] for r in results]
    assert len(expressions) == len(set(expressions))


def test_search_favorites_returns_list():
    with patch("crontab_buddy.fidelity_search.list_favorites", return_value=FAKE_FAVORITES):
        results = search_favorites_by_fidelity(0.0)
    assert isinstance(results, list)


def test_search_favorites_has_name_key():
    with patch("crontab_buddy.fidelity_search.list_favorites", return_value=FAKE_FAVORITES):
        results = search_favorites_by_fidelity(0.0)
    for r in results:
        assert "name" in r
        assert r["source"] == "favorites"


def test_search_above_score_combines_sources():
    with patch("crontab_buddy.fidelity_search.get_history", return_value=FAKE_HISTORY), \
         patch("crontab_buddy.fidelity_search.list_favorites", return_value=FAKE_FAVORITES):
        results = search_above_score(0.0)
    sources = {r["source"] for r in results}
    assert "history" in sources or "favorites" in sources


def test_search_above_score_no_duplicates():
    with patch("crontab_buddy.fidelity_search.get_history", return_value=FAKE_HISTORY), \
         patch("crontab_buddy.fidelity_search.list_favorites", return_value=FAKE_FAVORITES):
        results = search_above_score(0.0)
    expressions = [r["expression"] for r in results]
    assert len(expressions) == len(set(expressions))


def test_cmd_search_history_prints(capsys):
    with patch("crontab_buddy.fidelity_search.get_history", return_value=FAKE_HISTORY):
        cmd_fidelity_search_history(Args(0.0))
    out = capsys.readouterr().out
    assert "history" in out or "No" in out


def test_cmd_search_favorites_prints(capsys):
    with patch("crontab_buddy.fidelity_search.list_favorites", return_value=FAKE_FAVORITES):
        cmd_fidelity_search_favorites(Args(0.0))
    out = capsys.readouterr().out
    assert "favorites" in out or "No" in out


def test_cmd_search_all_no_results_message(capsys):
    with patch("crontab_buddy.fidelity_search.get_history", return_value=[]), \
         patch("crontab_buddy.fidelity_search.list_favorites", return_value=[]):
        cmd_fidelity_search_all(Args(0.99))
    out = capsys.readouterr().out
    assert "No" in out
