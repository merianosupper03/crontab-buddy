"""Tests for crontab_buddy/status.py"""

import pytest
from crontab_buddy.status import (
    set_status,
    get_status,
    delete_status,
    list_statuses,
    filter_by_status,
)


@pytest.fixture
def tmp_status(tmp_path):
    return str(tmp_path / "status.json")


def test_set_and_get(tmp_status):
    set_status("* * * * *", "active", tmp_status)
    assert get_status("* * * * *", tmp_status) == "active"


def test_get_missing_returns_none(tmp_status):
    assert get_status("0 5 * * *", tmp_status) is None


def test_overwrite_status(tmp_status):
    set_status("0 5 * * *", "active", tmp_status)
    set_status("0 5 * * *", "inactive", tmp_status)
    assert get_status("0 5 * * *", tmp_status) == "inactive"


def test_invalid_status_raises(tmp_status):
    with pytest.raises(ValueError, match="Invalid status"):
        set_status("* * * * *", "broken", tmp_status)


def test_delete_existing(tmp_status):
    set_status("0 0 * * *", "error", tmp_status)
    result = delete_status("0 0 * * *", tmp_status)
    assert result is True
    assert get_status("0 0 * * *", tmp_status) is None


def test_delete_missing_returns_false(tmp_status):
    assert delete_status("0 0 * * *", tmp_status) is False


def test_list_statuses_empty(tmp_status):
    assert list_statuses(tmp_status) == {}


def test_list_statuses_multiple(tmp_status):
    set_status("* * * * *", "active", tmp_status)
    set_status("0 5 * * *", "inactive", tmp_status)
    result = list_statuses(tmp_status)
    assert result["* * * * *"] == "active"
    assert result["0 5 * * *"] == "inactive"


def test_filter_by_status_returns_matching(tmp_status):
    set_status("* * * * *", "active", tmp_status)
    set_status("0 5 * * *", "inactive", tmp_status)
    set_status("0 0 * * 1", "active", tmp_status)
    active = filter_by_status("active", tmp_status)
    assert "* * * * *" in active
    assert "0 0 * * 1" in active
    assert "0 5 * * *" not in active


def test_filter_by_status_empty_result(tmp_status):
    set_status("* * * * *", "active", tmp_status)
    result = filter_by_status("error", tmp_status)
    assert result == []


def test_filter_by_invalid_status_raises(tmp_status):
    with pytest.raises(ValueError, match="Invalid status"):
        filter_by_status("unknown", tmp_status)


def test_all_valid_statuses_accepted(tmp_status):
    for i, status in enumerate(["active", "inactive", "error"]):
        expr = f"0 {i} * * *"
        set_status(expr, status, tmp_status)
        assert get_status(expr, tmp_status) == status
