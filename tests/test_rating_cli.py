"""Tests for a rating CLI module (cmd_rate_set, cmd_rate_get, cmd_rate_list)."""
import pytest
from unittest.mock import patch, MagicMock
from types import SimpleNamespace

# We'll test against a rating_cli module we're about to create
from crontab_buddy import rating_cli


@pytest.fixture
def tp(tmp_path):
    with patch("crontab_buddy.rating_cli.RATINGS_FILE", tmp_path / "ratings.json"):
        yield tmp_path


def args(**kwargs):
    defaults = {"expression": "0 9 * * 1", "score": 5, "comment": None}
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_cmd_rate_set_prints_saved(tp, capsys):
    rating_cli.cmd_rate_set(args(score=4, comment="nice"))
    out = capsys.readouterr().out
    assert "saved" in out.lower() or "rated" in out.lower()


def test_cmd_rate_set_invalid_score_prints_error(tp, capsys):
    rating_cli.cmd_rate_set(args(score=10))
    out = capsys.readouterr().out
    assert "invalid" in out.lower() or "error" in out.lower()


def test_cmd_rate_get_existing(tp, capsys):
    rating_cli.cmd_rate_set(args(score=3, comment=None))
    rating_cli.cmd_rate_get(args())
    out = capsys.readouterr().out
    assert "3" in out


def test_cmd_rate_get_missing(tp, capsys):
    rating_cli.cmd_rate_get(args())
    out = capsys.readouterr().out
    assert "no rating" in out.lower() or "not found" in out.lower()


def test_cmd_rate_list_empty(tp, capsys):
    rating_cli.cmd_rate_list(SimpleNamespace())
    out = capsys.readouterr().out
    assert "no" in out.lower() or out.strip() == ""


def test_cmd_rate_list_shows_entries(tp, capsys):
    rating_cli.cmd_rate_set(args(expression="0 9 * * 1", score=5, comment=None))
    rating_cli.cmd_rate_set(args(expression="*/5 * * * *", score=2, comment="frequent"))
    rating_cli.cmd_rate_list(SimpleNamespace())
    out = capsys.readouterr().out
    assert "0 9 * * 1" in out
    assert "*/5 * * * *" in out
