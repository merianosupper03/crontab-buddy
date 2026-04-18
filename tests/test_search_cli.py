import pytest
from unittest.mock import patch
from crontab_buddy.search_cli import (
    cmd_search_history, cmd_search_favorites, cmd_search_tag, cmd_search_all
)

SAMPLE_RESULTS = [
    {"expression": "0 9 * * 1", "description": "At 09on Monday", "source": "history", "timestamp": "2024-01-01"},
]

FAVn    {"name": "weekly", "expression": "0 9 * * 1", "description": "At 09:00 on Monday", "source": "favorites"},
]

TAG_RESULTS = [
    {"expression": "0 9 * * 1", "description": "At 09:00 on Monday", "tags": ["work"], "source": "tags"},
]


def test_cmd_search_history_prints_results(capsys):
    with patch("crontab_buddy.search_cli.search_history", return_value=SAMPLE_RESULTS):
        cmd_search_history("9")
    out = capsys.readouterr().out
    assert "0 9 * * 1" in out
    assert "history" in out


def test_cmd_search_history_no_results(capsys):
    with patch("crontab_buddy.search_cli.search_history", return_value=[]):
        cmd_search_history("zzz")
    out = capsys.readouterr().out
    assert "No results" in out


def test_cmd_search_favorites_prints_name(capsys):
    with patch("crontab_buddy.search_cli.search_favorites", return_value=FAV_RESULTS):
        cmd_search_favorites("weekly")
    out = capsys.readouterr().out
    assert "weekly" in out
    assert "0 9 * * 1" in out


def test_cmd_search_tag_prints_tags(capsys):
    with patch("crontab_buddy.search_cli.search_by_tag", return_value=TAG_RESULTS):
        cmd_search_tag("work")
    out = capsys.readouterr().out
    assert "work" in out
    assert "0 9 * * 1" in out


def test_cmd_search_all_prints_combined(capsys):
    with patch("crontab_buddy.search_cli.search_all", return_value=SAMPLE_RESULTS):
        cmd_search_all("9")
    out = capsys.readouterr().out
    assert "0 9 * * 1" in out


def test_cmd_search_all_no_results(capsys):
    with patch("crontab_buddy.search_cli.search_all", return_value=[]):
        cmd_search_all("nothing")
    out = capsys.readouterr().out
    assert "No results" in out
