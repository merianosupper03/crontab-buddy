"""Tests for crontab_buddy.audit"""

import pytest
from crontab_buddy.audit import log_action, get_audit_log, clear_audit_log


@pytest.fixture
def tmp_audit(tmp_path):
    return str(tmp_path / "audit.json")


def test_log_and_retrieve(tmp_audit):
    log_action("validate", "* * * * *", path=tmp_audit)
    entries = get_audit_log(path=tmp_audit)
    assert len(entries) == 1
    assert entries[0]["action"] == "validate"
    assert entries[0]["expression"] == "* * * * *"


def test_log_multiple_entries(tmp_audit):
    log_action("validate", "* * * * *", path=tmp_audit)
    log_action("export", "0 9 * * 1", path=tmp_audit)
    entries = get_audit_log(path=tmp_audit)
    assert len(entries) == 2


def test_log_with_detail(tmp_audit):
    log_action("lint", "*/1 * * * *", detail="every minute warning", path=tmp_audit)
    entries = get_audit_log(path=tmp_audit)
    assert entries[0]["detail"] == "every minute warning"


def test_filter_by_action(tmp_audit):
    log_action("validate", "* * * * *", path=tmp_audit)
    log_action("export", "0 9 * * 1", path=tmp_audit)
    log_action("validate", "0 0 * * *", path=tmp_audit)
    results = get_audit_log(action_filter="validate", path=tmp_audit)
    assert len(results) == 2
    assert all(r["action"] == "validate" for r in results)


def test_filter_no_match(tmp_audit):
    log_action("validate", "* * * * *", path=tmp_audit)
    results = get_audit_log(action_filter="export", path=tmp_audit)
    assert results == []


def test_clear_audit_log(tmp_audit):
    log_action("validate", "* * * * *", path=tmp_audit)
    clear_audit_log(path=tmp_audit)
    assert get_audit_log(path=tmp_audit) == []


def test_timestamp_present(tmp_audit):
    log_action("validate", "* * * * *", path=tmp_audit)
    entry = get_audit_log(path=tmp_audit)[0]
    assert "timestamp" in entry
    assert "T" in entry["timestamp"]  # ISO format check


def test_empty_log_returns_empty_list(tmp_audit):
    assert get_audit_log(path=tmp_audit) == []
