"""Tests for crontab_buddy.webhook."""

import pytest
from crontab_buddy.webhook import (
    set_webhook,
    get_webhook,
    delete_webhook,
    list_webhooks,
)


@pytest.fixture
def tmp_webhook(tmp_path):
    return str(tmp_path / "webhooks.json")


def test_set_and_get(tmp_webhook):
    set_webhook("0 9 * * 1", "https://example.com/hook", path=tmp_webhook)
    entry = get_webhook("0 9 * * 1", path=tmp_webhook)
    assert entry is not None
    assert entry["url"] == "https://example.com/hook"


def test_get_missing_returns_none(tmp_webhook):
    assert get_webhook("* * * * *", path=tmp_webhook) is None


def test_invalid_url_raises(tmp_webhook):
    with pytest.raises(ValueError, match="Invalid webhook URL"):
        set_webhook("* * * * *", "ftp://bad.url", path=tmp_webhook)


def test_overwrite_webhook(tmp_webhook):
    set_webhook("0 0 * * *", "https://first.com", path=tmp_webhook)
    set_webhook("0 0 * * *", "https://second.com", path=tmp_webhook)
    entry = get_webhook("0 0 * * *", path=tmp_webhook)
    assert entry["url"] == "https://second.com"


def test_default_flags_are_true(tmp_webhook):
    set_webhook("*/5 * * * *", "https://hook.io/x", path=tmp_webhook)
    entry = get_webhook("*/5 * * * *", path=tmp_webhook)
    assert entry["on_success"] is True
    assert entry["on_failure"] is True


def test_custom_flags(tmp_webhook):
    set_webhook(
        "0 12 * * *",
        "https://hook.io/y",
        on_success=False,
        on_failure=True,
        path=tmp_webhook,
    )
    entry = get_webhook("0 12 * * *", path=tmp_webhook)
    assert entry["on_success"] is False
    assert entry["on_failure"] is True


def test_delete_existing(tmp_webhook):
    set_webhook("0 6 * * *", "https://del.me", path=tmp_webhook)
    result = delete_webhook("0 6 * * *", path=tmp_webhook)
    assert result is True
    assert get_webhook("0 6 * * *", path=tmp_webhook) is None


def test_delete_missing_returns_false(tmp_webhook):
    assert delete_webhook("1 2 3 4 5", path=tmp_webhook) is False


def test_list_webhooks_empty(tmp_webhook):
    assert list_webhooks(path=tmp_webhook) == {}


def test_list_webhooks_multiple(tmp_webhook):
    set_webhook("0 1 * * *", "https://a.com", path=tmp_webhook)
    set_webhook("0 2 * * *", "https://b.com", path=tmp_webhook)
    entries = list_webhooks(path=tmp_webhook)
    assert len(entries) == 2
    assert "0 1 * * *" in entries
    assert "0 2 * * *" in entries
