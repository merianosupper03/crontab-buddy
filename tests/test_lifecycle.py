"""Tests for crontab_buddy.lifecycle."""

import json
import os
import pytest

from crontab_buddy import lifecycle as lc


@pytest.fixture
def tmp_lifecycle(tmp_path, monkeypatch):
    path = str(tmp_path / "lifecycle.json")
    monkeypatch.setattr(lc, "_DATA_FILE", path)
    return path


def test_set_and_get(tmp_lifecycle):
    lc.set_lifecycle("0 * * * *", "active")
    info = lc.get_lifecycle("0 * * * *")
    assert info is not None
    assert info["state"] == "active"


def test_get_missing_returns_none(tmp_lifecycle):
    assert lc.get_lifecycle("* * * * *") is None


def test_overwrite_lifecycle(tmp_lifecycle):
    lc.set_lifecycle("0 * * * *", "draft")
    lc.set_lifecycle("0 * * * *", "active")
    info = lc.get_lifecycle("0 * * * *")
    assert info["state"] == "active"
    assert info["previous_state"] == "draft"


def test_invalid_state_raises(tmp_lifecycle):
    with pytest.raises(ValueError, match="Invalid state"):
        lc.set_lifecycle("0 * * * *", "unknown")


def test_all_valid_states_accepted(tmp_lifecycle):
    for state in lc.VALID_STATES:
        lc.set_lifecycle("0 * * * *", state)
        info = lc.get_lifecycle("0 * * * *")
        assert info["state"] == state


def test_delete_existing(tmp_lifecycle):
    lc.set_lifecycle("0 * * * *", "retired")
    assert lc.delete_lifecycle("0 * * * *") is True
    assert lc.get_lifecycle("0 * * * *") is None


def test_delete_missing_returns_false(tmp_lifecycle):
    assert lc.delete_lifecycle("0 * * * *") is False


def test_reason_stored(tmp_lifecycle):
    lc.set_lifecycle("0 * * * *", "deprecated", reason="replaced by new job")
    info = lc.get_lifecycle("0 * * * *")
    assert info["reason"] == "replaced by new job"


def test_list_by_state(tmp_lifecycle):
    lc.set_lifecycle("0 * * * *", "active")
    lc.set_lifecycle("0 0 * * *", "draft")
    lc.set_lifecycle("0 0 1 * *", "active")
    active = lc.list_by_state("active")
    assert len(active) == 2
    exprs = {e["expression"] for e in active}
    assert "0 * * * *" in exprs
    assert "0 0 1 * *" in exprs


def test_list_by_invalid_state_raises(tmp_lifecycle):
    with pytest.raises(ValueError):
        lc.list_by_state("nonexistent")


def test_list_all(tmp_lifecycle):
    lc.set_lifecycle("0 * * * *", "active")
    lc.set_lifecycle("0 0 * * *", "retired")
    all_entries = lc.list_all_lifecycles()
    assert len(all_entries) == 2


def test_updated_at_is_set(tmp_lifecycle):
    lc.set_lifecycle("0 * * * *", "active")
    info = lc.get_lifecycle("0 * * * *")
    assert "updated_at" in info
    assert info["updated_at"]  # non-empty
