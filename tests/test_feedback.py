"""Tests for crontab_buddy.feedback."""
import pytest

from crontab_buddy.feedback import (
    add_feedback,
    delete_feedback,
    feedback_summary,
    get_feedback,
    list_all_feedback,
)


@pytest.fixture()
def tmp_feedback(tmp_path):
    return str(tmp_path / "feedback.json")


def test_add_and_get(tmp_feedback):
    add_feedback("* * * * *", "positive", path=tmp_feedback)
    entries = get_feedback("* * * * *", path=tmp_feedback)
    assert len(entries) == 1
    assert entries[0]["sentiment"] == "positive"


def test_get_missing_returns_empty(tmp_feedback):
    assert get_feedback("0 * * * *", path=tmp_feedback) == []


def test_add_with_comment(tmp_feedback):
    add_feedback("0 9 * * 1", "neutral", comment="runs weekly", path=tmp_feedback)
    entries = get_feedback("0 9 * * 1", path=tmp_feedback)
    assert entries[0]["comment"] == "runs weekly"


def test_multiple_entries_same_expression(tmp_feedback):
    add_feedback("*/5 * * * *", "positive", path=tmp_feedback)
    add_feedback("*/5 * * * *", "negative", comment="too frequent", path=tmp_feedback)
    entries = get_feedback("*/5 * * * *", path=tmp_feedback)
    assert len(entries) == 2


def test_invalid_sentiment_raises(tmp_feedback):
    with pytest.raises(ValueError):
        add_feedback("* * * * *", "great", path=tmp_feedback)


def test_delete_existing(tmp_feedback):
    add_feedback("0 0 * * *", "negative", path=tmp_feedback)
    assert delete_feedback("0 0 * * *", path=tmp_feedback) is True
    assert get_feedback("0 0 * * *", path=tmp_feedback) == []


def test_delete_missing_returns_false(tmp_feedback):
    assert delete_feedback("0 0 * * *", path=tmp_feedback) is False


def test_list_all_feedback(tmp_feedback):
    add_feedback("* * * * *", "positive", path=tmp_feedback)
    add_feedback("0 12 * * *", "neutral", path=tmp_feedback)
    all_fb = list_all_feedback(path=tmp_feedback)
    assert "* * * * *" in all_fb
    assert "0 12 * * *" in all_fb


def test_feedback_summary_counts(tmp_feedback):
    add_feedback("0 6 * * *", "positive", path=tmp_feedback)
    add_feedback("0 6 * * *", "positive", path=tmp_feedback)
    add_feedback("0 6 * * *", "negative", path=tmp_feedback)
    summary = feedback_summary("0 6 * * *", path=tmp_feedback)
    assert summary["positive"] == 2
    assert summary["negative"] == 1
    assert summary["neutral"] == 0
    assert summary["total"] == 3


def test_feedback_summary_empty(tmp_feedback):
    summary = feedback_summary("1 2 3 4 5", path=tmp_feedback)
    assert summary["total"] == 0


def test_timestamp_stored(tmp_feedback):
    add_feedback("*/10 * * * *", "neutral", path=tmp_feedback)
    entries = get_feedback("*/10 * * * *", path=tmp_feedback)
    assert "timestamp" in entries[0]
    assert entries[0]["timestamp"] != ""
