"""Tests for crontab_buddy.trigger module."""

import pytest
from crontab_buddy.trigger import (
    set_trigger,
    get_trigger,
    delete_trigger,
    list_triggers,
    VALID_EVENTS,
)


@pytest.fixture
def tmp_trigger(tmp_path):
    return str(tmp_path / "triggers.json")


def test_set_and_get(tmp_trigger):
    set_trigger("0 9 * * *", "success", path=tmp_trigger)
    rule = get_trigger("0 9 * * *", path=tmp_trigger)
    assert rule is not None
    assert rule["event"] == "success"


def test_get_missing_returns_none(tmp_trigger):
    assert get_trigger("* * * * *", path=tmp_trigger) is None


def test_invalid_event_raises(tmp_trigger):
    with pytest.raises(ValueError, match="Invalid event"):
        set_trigger("0 9 * * *", "unknown_event", path=tmp_trigger)


def test_all_valid_events_accepted(tmp_trigger):
    for event in VALID_EVENTS:
        set_trigger("0 0 * * *", event, path=tmp_trigger)
        rule = get_trigger("0 0 * * *", path=tmp_trigger)
        assert rule["event"] == event


def test_set_with_condition(tmp_trigger):
    set_trigger("*/5 * * * *", "failure", condition="exit_code != 0", path=tmp_trigger)
    rule = get_trigger("*/5 * * * *", path=tmp_trigger)
    assert rule["condition"] == "exit_code != 0"


def test_overwrite_trigger(tmp_trigger):
    set_trigger("0 12 * * *", "success", path=tmp_trigger)
    set_trigger("0 12 * * *", "failure", path=tmp_trigger)
    rule = get_trigger("0 12 * * *", path=tmp_trigger)
    assert rule["event"] == "failure"


def test_delete_existing(tmp_trigger):
    set_trigger("0 6 * * *", "always", path=tmp_trigger)
    result = delete_trigger("0 6 * * *", path=tmp_trigger)
    assert result is True
    assert get_trigger("0 6 * * *", path=tmp_trigger) is None


def test_delete_missing_returns_false(tmp_trigger):
    assert delete_trigger("0 1 * * *", path=tmp_trigger) is False


def test_list_triggers_empty(tmp_trigger):
    assert list_triggers(path=tmp_trigger) == []


def test_list_triggers_multiple(tmp_trigger):
    set_trigger("0 9 * * *", "success", path=tmp_trigger)
    set_trigger("0 18 * * *", "failure", path=tmp_trigger)
    rules = list_triggers(path=tmp_trigger)
    assert len(rules) == 2
    expressions = [r["expression"] for r in rules]
    assert "0 9 * * *" in expressions
    assert "0 18 * * *" in expressions


def test_list_triggers_has_event_key(tmp_trigger):
    set_trigger("0 3 * * *", "manual", path=tmp_trigger)
    rules = list_triggers(path=tmp_trigger)
    assert rules[0]["event"] == "manual"
