"""Tests for density_score_search_cli."""
import pytest
from unittest.mock import patch
from io import StringIO
import sys

from crontab_buddy.density_score_search_cli import (
    cmd_density_score_search_history,
    cmd_density_score_search_favorites,
    cmd_density_score_search_all,
)


class Args:
    def __init__(self, min_score="0.5"):
        self.min_score = min_score


@pytest.fixture
def captured(capsys):
    return capsys


def _fake_results(source="history"):
    return [
        {
            "expression": "* * * * *",
            "description": "Every minute",
            "grade": "packed",
            "score": 1.0,
            "source": source,
        }
    ]


def test_cmd_search_history_prints_results(captured):
    with patch(
        "crontab_buddy.density_score_search_cli.search_history_by_density_score",
        return_value=_fake_results("history"),
    ):
        cmd_density_score_search_history(Args(min_score="0.5"))
    out = captured.readouterr().out
    assert "* * * * *" in out
    assert "packed" in out


def test_cmd_search_history_no_results(captured):
    with patch(
        "crontab_buddy.density_score_search_cli.search_history_by_density_score",
        return_value=[],
    ):
        cmd_density_score_search_history(Args(min_score="0.9"))
    out = captured.readouterr().out
    assert "No history results found" in out


def test_cmd_search_history_invalid_score_prints_error(captured):
    cmd_density_score_search_history(Args(min_score="not_a_float"))
    out = captured.readouterr().out
    assert "Error" in out


def test_cmd_search_favorites_prints_results(captured):
    with patch(
        "crontab_buddy.density_score_search_cli.search_favorites_by_density_score",
        return_value=_fake_results("favorites"),
    ):
        cmd_density_score_search_favorites(Args(min_score="0.5"))
    out = captured.readouterr().out
    assert "favorites" in out
    assert "* * * * *" in out


def test_cmd_search_favorites_invalid_score_prints_error(captured):
    cmd_density_score_search_favorites(Args(min_score="bad"))
    out = captured.readouterr().out
    assert "Error" in out


def test_cmd_search_all_combines_results(captured):
    hist = _fake_results("history")
    favs = _fake_results("favorites")
    with patch(
        "crontab_buddy.density_score_search_cli.search_history_by_density_score",
        return_value=hist,
    ), patch(
        "crontab_buddy.density_score_search_cli.search_favorites_by_density_score",
        return_value=favs,
    ):
        cmd_density_score_search_all(Args(min_score="0.5"))
    out = captured.readouterr().out
    assert out.count("* * * * *") == 2


def test_cmd_search_all_invalid_score_prints_error(captured):
    cmd_density_score_search_all(Args(min_score="???"))
    out = captured.readouterr().out
    assert "Error" in out
