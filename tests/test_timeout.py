"""Tests for crontab_buddy.timeout."""
import pytest

from crontab_buddy.timeout import (
    delete_timeout,
    get_timeout,
    list_timeouts,
    set_timeout,
)


@pytest.fixture
def tmp_timeout(tmp_path):
    return str(tmp_path / "timeouts.json")


def test_set_and_get(tmp_timeout):
    set_timeout("0 * * * *", 120, path=tmp_timeout)
    result = get_timeout("0 * * * *", path=tmp_timeout)
    assert result is not None
    assert result["seconds"] == 120
    assert result["action"] == "kill"


def test_get_missing_returns_none(tmp_timeout):
    assert get_timeout("* * * * *", path=tmp_timeout) is None


def test_overwrite_timeout(tmp_timeout):
    set_timeout("0 * * * *", 60, path=tmp_timeout)
    set_timeout("0 * * * *", 300, action="notify", path=tmp_timeout)
    result = get_timeout("0 * * * *", path=tmp_timeout)
    assert result["seconds"] == 300
    assert result["action"] == "notify"


def test_invalid_seconds_raises(tmp_timeout):
    with pytest.raises(ValueError, match="positive"):
        set_timeout("0 * * * *", 0, path=tmp_timeout)
    with pytest.raises(ValueError, match="positive"):
        set_timeout("0 * * * *", -5, path=tmp_timeout)


def test_invalid_action_raises(tmp_timeout):
    with pytest.raises(ValueError, match="action"):
        set_timeout("0 * * * *", 60, action="email", path=tmp_timeout)


def test_delete_existing(tmp_timeout):
    set_timeout("0 * * * *", 60, path=tmp_timeout)
    assert delete_timeout("0 * * * *", path=tmp_timeout) is True
    assert get_timeout("0 * * * *", path=tmp_timeout) is None


def test_delete_missing_returns_false(tmp_timeout):
    assert delete_timeout("0 * * * *", path=tmp_timeout) is False


def test_list_timeouts_empty(tmp_timeout):
    assert list_timeouts(path=tmp_timeout) == {}


def test_list_timeouts_multiple(tmp_timeout):
    set_timeout("0 * * * *", 60, path=tmp_timeout)
    set_timeout("*/5 * * * *", 30, action="notify", path=tmp_timeout)
    result = list_timeouts(path=tmp_timeout)
    assert len(result) == 2
    assert "0 * * * *" in result
    assert "*/5 * * * *" in result


def test_default_action_is_kill(tmp_timeout):
    set_timeout("0 0 * * *", 90, path=tmp_timeout)
    result = get_timeout("0 0 * * *", path=tmp_timeout)
    assert result["action"] == "kill"
