"""Tests for crontab_buddy.pause."""

import pytest
from pathlib import Path
from crontab_buddy.pause import (
    pause_expression,
    resume_expression,
    is_paused,
    get_pause_info,
    list_paused,
    clear_paused,
)


@pytest.fixture
def tmp_pause(tmp_path):
    return tmp_path / "paused.json"


def test_pause_new_expression(tmp_pause):
    result = pause_expression("0 * * * *", path=tmp_pause)
    assert result is True


def test_pause_duplicate_returns_false(tmp_pause):
    pause_expression("0 * * * *", path=tmp_pause)
    result = pause_expression("0 * * * *", path=tmp_pause)
    assert result is False


def test_is_paused_true(tmp_pause):
    pause_expression("0 * * * *", path=tmp_pause)
    assert is_paused("0 * * * *", path=tmp_pause) is True


def test_is_paused_false(tmp_pause):
    assert is_paused("0 * * * *", path=tmp_pause) is False


def test_resume_existing(tmp_pause):
    pause_expression("0 * * * *", path=tmp_pause)
    result = resume_expression("0 * * * *", path=tmp_pause)
    assert result is True
    assert is_paused("0 * * * *", path=tmp_pause) is False


def test_resume_missing_returns_false(tmp_pause):
    result = resume_expression("0 * * * *", path=tmp_pause)
    assert result is False


def test_pause_with_reason(tmp_pause):
    pause_expression("*/5 * * * *", reason="maintenance window", path=tmp_pause)
    info = get_pause_info("*/5 * * * *", path=tmp_pause)
    assert info is not None
    assert info["reason"] == "maintenance window"


def test_pause_without_reason_stores_empty_string(tmp_pause):
    pause_expression("0 9 * * 1", path=tmp_pause)
    info = get_pause_info("0 9 * * 1", path=tmp_pause)
    assert info["reason"] == ""


def test_get_pause_info_missing_returns_none(tmp_pause):
    result = get_pause_info("0 9 * * 1", path=tmp_pause)
    assert result is None


def test_list_paused_multiple(tmp_pause):
    pause_expression("0 * * * *", path=tmp_pause)
    pause_expression("*/10 * * * *", reason="low priority", path=tmp_pause)
    paused = list_paused(path=tmp_pause)
    assert len(paused) == 2
    assert "0 * * * *" in paused
    assert "*/10 * * * *" in paused


def test_list_paused_empty(tmp_pause):
    assert list_paused(path=tmp_pause) == {}


def test_clear_paused(tmp_pause):
    pause_expression("0 * * * *", path=tmp_pause)
    pause_expression("*/5 * * * *", path=tmp_pause)
    clear_paused(path=tmp_pause)
    assert list_paused(path=tmp_pause) == {}


def test_pause_strips_whitespace(tmp_pause):
    pause_expression("  0 * * * *  ", path=tmp_pause)
    assert is_paused("0 * * * *", path=tmp_pause) is True
