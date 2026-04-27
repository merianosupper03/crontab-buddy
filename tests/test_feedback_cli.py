"""Tests for crontab_buddy.feedback_cli."""
import pytest

from crontab_buddy.feedback import add_feedback
from crontab_buddy.feedback_cli import (
    cmd_feedback_add,
    cmd_feedback_delete,
    cmd_feedback_get,
    cmd_feedback_list,
    cmd_feedback_summary,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture()
def tp(tmp_path):
    return str(tmp_path / "feedback.json")


def test_cmd_add_prints(tp, capsys):
    args = Args(expression="* * * * *", sentiment="positive", comment="")
    cmd_feedback_add(args, path=tp)
    out = capsys.readouterr().out
    assert "Feedback recorded" in out
    assert "positive" in out


def test_cmd_add_invalid_sentiment_prints_error(tp, capsys):
    args = Args(expression="* * * * *", sentiment="amazing", comment="")
    cmd_feedback_add(args, path=tp)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_get_existing(tp, capsys):
    add_feedback("0 9 * * 1", "neutral", comment="weekly", path=tp)
    args = Args(expression="0 9 * * 1")
    cmd_feedback_get(args, path=tp)
    out = capsys.readouterr().out
    assert "neutral" in out
    assert "weekly" in out


def test_cmd_get_missing(tp, capsys):
    args = Args(expression="1 2 3 4 5")
    cmd_feedback_get(args, path=tp)
    out = capsys.readouterr().out
    assert "No feedback" in out


def test_cmd_delete_success(tp, capsys):
    add_feedback("*/5 * * * *", "negative", path=tp)
    args = Args(expression="*/5 * * * *")
    cmd_feedback_delete(args, path=tp)
    out = capsys.readouterr().out
    assert "deleted" in out


def test_cmd_delete_missing(tp, capsys):
    args = Args(expression="*/5 * * * *")
    cmd_feedback_delete(args, path=tp)
    out = capsys.readouterr().out
    assert "No feedback found" in out


def test_cmd_summary_prints(tp, capsys):
    add_feedback("0 0 * * *", "positive", path=tp)
    add_feedback("0 0 * * *", "negative", path=tp)
    args = Args(expression="0 0 * * *")
    cmd_feedback_summary(args, path=tp)
    out = capsys.readouterr().out
    assert "positive" in out
    assert "total" in out


def test_cmd_list_with_entries(tp, capsys):
    add_feedback("* * * * *", "positive", path=tp)
    add_feedback("0 12 * * *", "neutral", path=tp)
    cmd_feedback_list(None, path=tp)
    out = capsys.readouterr().out
    assert "* * * * *" in out
    assert "0 12 * * *" in out


def test_cmd_list_empty(tp, capsys):
    cmd_feedback_list(None, path=tp)
    out = capsys.readouterr().out
    assert "No feedback" in out
