"""Tests for crontab_buddy.notify."""
import pytest

from crontab_buddy.notify import (
    set_notify,
    get_notify,
    delete_notify,
    list_notify,
)


@pytest.fixture
def tmp_notify(tmp_path):
    return str(tmp_path / "notify.json")


def test_set_and_get(tmp_notify):
    set_notify("0 9 * * *", "alice@example.com", "failure", path=tmp_notify)
    result = get_notify("0 9 * * *", path=tmp_notify)
    assert result is not None
    assert result["email"] == "alice@example.com"
    assert result["event"] == "failure"


def test_get_missing_returns_none(tmp_notify):
    assert get_notify("* * * * *", path=tmp_notify) is None


def test_default_event_is_failure(tmp_notify):
    set_notify("0 8 * * *", "bob@example.com", path=tmp_notify)
    result = get_notify("0 8 * * *", path=tmp_notify)
    assert result["event"] == "failure"


def test_overwrite_notify(tmp_notify):
    set_notify("0 9 * * *", "old@example.com", path=tmp_notify)
    set_notify("0 9 * * *", "new@example.com", "always", path=tmp_notify)
    result = get_notify("0 9 * * *", path=tmp_notify)
    assert result["email"] == "new@example.com"
    assert result["event"] == "always"


def test_invalid_event_raises(tmp_notify):
    with pytest.raises(ValueError, match="Invalid event"):
        set_notify("0 9 * * *", "x@example.com", "never", path=tmp_notify)


def test_delete_existing(tmp_notify):
    set_notify("0 9 * * *", "alice@example.com", path=tmp_notify)
    assert delete_notify("0 9 * * *", path=tmp_notify) is True
    assert get_notify("0 9 * * *", path=tmp_notify) is None


def test_delete_missing_returns_false(tmp_notify):
    assert delete_notify("0 9 * * *", path=tmp_notify) is False


def test_list_notify_empty(tmp_notify):
    assert list_notify(path=tmp_notify) == []


def test_list_notify_multiple(tmp_notify):
    set_notify("0 9 * * *", "a@example.com", "always", path=tmp_notify)
    set_notify("0 12 * * *", "b@example.com", "success", path=tmp_notify)
    entries = list_notify(path=tmp_notify)
    assert len(entries) == 2
    exprs = {e["expression"] for e in entries}
    assert "0 9 * * *" in exprs
    assert "0 12 * * *" in exprs


def test_list_notify_has_all_keys(tmp_notify):
    set_notify("0 9 * * *", "a@example.com", "failure", path=tmp_notify)
    entry = list_notify(path=tmp_notify)[0]
    assert "expression" in entry
    assert "email" in entry
    assert "event" in entry
