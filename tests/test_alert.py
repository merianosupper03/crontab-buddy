"""Tests for crontab_buddy.alert module."""
import pytest
from crontab_buddy.alert import (
    set_alert,
    get_alert,
    delete_alert,
    list_alerts,
)


@pytest.fixture
def tmp_alert(tmp_path):
    return str(tmp_path / "alerts.json")


def test_set_and_get(tmp_alert):
    set_alert("0 9 * * *", "email", "failure", "ops@example.com", path=tmp_alert)
    result = get_alert("0 9 * * *", path=tmp_alert)
    assert result is not None
    assert result["channel"] == "email"
    assert result["event"] == "failure"
    assert result["target"] == "ops@example.com"


def test_get_missing_returns_none(tmp_alert):
    assert get_alert("* * * * *", path=tmp_alert) is None


def test_default_event_is_failure(tmp_alert):
    set_alert("*/5 * * * *", "slack", path=tmp_alert)
    result = get_alert("*/5 * * * *", path=tmp_alert)
    assert result["event"] == "failure"


def test_overwrite_alert(tmp_alert):
    set_alert("0 * * * *", "email", "failure", path=tmp_alert)
    set_alert("0 * * * *", "slack", "any", path=tmp_alert)
    result = get_alert("0 * * * *", path=tmp_alert)
    assert result["channel"] == "slack"
    assert result["event"] == "any"


def test_invalid_channel_raises(tmp_alert):
    with pytest.raises(ValueError, match="Invalid channel"):
        set_alert("0 9 * * *", "sms", path=tmp_alert)


def test_invalid_event_raises(tmp_alert):
    with pytest.raises(ValueError, match="Invalid event"):
        set_alert("0 9 * * *", "email", "never", path=tmp_alert)


def test_delete_existing(tmp_alert):
    set_alert("0 9 * * *", "log", path=tmp_alert)
    assert delete_alert("0 9 * * *", path=tmp_alert) is True
    assert get_alert("0 9 * * *", path=tmp_alert) is None


def test_delete_missing_returns_false(tmp_alert):
    assert delete_alert("0 9 * * *", path=tmp_alert) is False


def test_list_alerts_all_entries(tmp_alert):
    set_alert("0 9 * * *", "email", path=tmp_alert)
    set_alert("*/5 * * * *", "slack", "any", path=tmp_alert)
    alerts = list_alerts(path=tmp_alert)
    assert "0 9 * * *" in alerts
    assert "*/5 * * * *" in alerts


def test_all_valid_channels_accepted(tmp_alert):
    from crontab_buddy.alert import VALID_CHANNELS
    for i, ch in enumerate(VALID_CHANNELS):
        expr = f"{i} * * * *"
        set_alert(expr, ch, path=tmp_alert)
        assert get_alert(expr, path=tmp_alert)["channel"] == ch
