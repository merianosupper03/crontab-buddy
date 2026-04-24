"""Tests for crontab_buddy.escalation."""

import pytest
from crontab_buddy.escalation import (
    delete_escalation,
    get_escalation,
    list_escalations,
    set_escalation,
)


@pytest.fixture
def tmp_esc(tmp_path):
    return str(tmp_path / "escalations.json")


def test_set_and_get(tmp_esc):
    set_escalation("0 9 * * 1", "high", "email", "ops@example.com", path=tmp_esc)
    policy = get_escalation("0 9 * * 1", path=tmp_esc)
    assert policy is not None
    assert policy["level"] == "high"
    assert policy["channel"] == "email"
    assert policy["contact"] == "ops@example.com"


def test_get_missing_returns_none(tmp_esc):
    assert get_escalation("* * * * *", path=tmp_esc) is None


def test_overwrite_escalation(tmp_esc):
    set_escalation("0 9 * * 1", "low", "slack", "#alerts", path=tmp_esc)
    set_escalation("0 9 * * 1", "critical", "pagerduty", "team-oncall", path=tmp_esc)
    policy = get_escalation("0 9 * * 1", path=tmp_esc)
    assert policy["level"] == "critical"
    assert policy["channel"] == "pagerduty"


def test_invalid_level_raises(tmp_esc):
    with pytest.raises(ValueError, match="Invalid level"):
        set_escalation("* * * * *", "urgent", "email", "x@y.com", path=tmp_esc)


def test_invalid_channel_raises(tmp_esc):
    with pytest.raises(ValueError, match="Invalid channel"):
        set_escalation("* * * * *", "high", "fax", "x@y.com", path=tmp_esc)


def test_empty_contact_raises(tmp_esc):
    with pytest.raises(ValueError, match="Contact"):
        set_escalation("* * * * *", "high", "email", "   ", path=tmp_esc)


def test_delete_existing(tmp_esc):
    set_escalation("0 0 * * *", "medium", "slack", "#ops", path=tmp_esc)
    assert delete_escalation("0 0 * * *", path=tmp_esc) is True
    assert get_escalation("0 0 * * *", path=tmp_esc) is None


def test_delete_missing_returns_false(tmp_esc):
    assert delete_escalation("0 0 * * *", path=tmp_esc) is False


def test_list_escalations_all_present(tmp_esc):
    set_escalation("0 9 * * 1", "high", "email", "a@b.com", path=tmp_esc)
    set_escalation("0 0 * * *", "low", "slack", "#chan", path=tmp_esc)
    result = list_escalations(path=tmp_esc)
    assert "0 9 * * 1" in result
    assert "0 0 * * *" in result


def test_list_escalations_empty(tmp_esc):
    assert list_escalations(path=tmp_esc) == {}


def test_all_valid_levels_accepted(tmp_esc):
    from crontab_buddy.escalation import VALID_LEVELS
    for i, level in enumerate(VALID_LEVELS):
        expr = f"0 {i} * * *"
        set_escalation(expr, level, "email", "x@y.com", path=tmp_esc)
        policy = get_escalation(expr, path=tmp_esc)
        assert policy["level"] == level
