"""Tests for crontab_buddy.sla and crontab_buddy.sla_cli."""

from __future__ import annotations

import pytest

from crontab_buddy.sla import (
    VALID_POLICIES,
    check_sla,
    delete_sla,
    get_sla,
    list_slas,
    set_sla,
)


@pytest.fixture()
def tmp_sla(tmp_path):
    return str(tmp_path / "sla.json")


def test_set_and_get(tmp_sla):
    set_sla("* * * * *", 30, path=tmp_sla)
    entry = get_sla("* * * * *", path=tmp_sla)
    assert entry is not None
    assert entry["max_duration_seconds"] == 30
    assert entry["policy"] == "strict"


def test_get_missing_returns_none(tmp_sla):
    assert get_sla("0 * * * *", path=tmp_sla) is None


def test_overwrite_sla(tmp_sla):
    set_sla("0 0 * * *", 60, path=tmp_sla)
    set_sla("0 0 * * *", 120, policy="relaxed", path=tmp_sla)
    entry = get_sla("0 0 * * *", path=tmp_sla)
    assert entry["max_duration_seconds"] == 120
    assert entry["policy"] == "relaxed"


def test_invalid_max_seconds_raises(tmp_sla):
    with pytest.raises(ValueError):
        set_sla("* * * * *", 0, path=tmp_sla)
    with pytest.raises(ValueError):
        set_sla("* * * * *", -5, path=tmp_sla)


def test_invalid_policy_raises(tmp_sla):
    with pytest.raises(ValueError):
        set_sla("* * * * *", 30, policy="unknown", path=tmp_sla)


def test_all_valid_policies_accepted(tmp_sla):
    for i, policy in enumerate(VALID_POLICIES):
        expr = f"{i} * * * *"
        entry = set_sla(expr, 10, policy=policy, path=tmp_sla)
        assert entry["policy"] == policy


def test_set_with_note(tmp_sla):
    set_sla("0 6 * * 1", 45, note="weekly job", path=tmp_sla)
    entry = get_sla("0 6 * * 1", path=tmp_sla)
    assert entry["note"] == "weekly job"


def test_delete_existing(tmp_sla):
    set_sla("5 4 * * *", 20, path=tmp_sla)
    assert delete_sla("5 4 * * *", path=tmp_sla) is True
    assert get_sla("5 4 * * *", path=tmp_sla) is None


def test_delete_missing_returns_false(tmp_sla):
    assert delete_sla("1 2 3 4 5", path=tmp_sla) is False


def test_list_slas_empty(tmp_sla):
    assert list_slas(path=tmp_sla) == {}


def test_list_slas_multiple(tmp_sla):
    set_sla("* * * * *", 10, path=tmp_sla)
    set_sla("0 * * * *", 60, path=tmp_sla)
    entries = list_slas(path=tmp_sla)
    assert len(entries) == 2


def test_check_sla_ok(tmp_sla):
    set_sla("0 0 * * *", 100, path=tmp_sla)
    result = check_sla("0 0 * * *", 50, path=tmp_sla)
    assert result["violated"] is False
    assert result["status"] == "ok"


def test_check_sla_violated(tmp_sla):
    set_sla("0 0 * * *", 30, path=tmp_sla)
    result = check_sla("0 0 * * *", 60, path=tmp_sla)
    assert result["violated"] is True
    assert result["status"] == "violated"


def test_check_sla_no_sla(tmp_sla):
    result = check_sla("1 1 1 1 1", 5, path=tmp_sla)
    assert result["status"] == "no_sla"
    assert result["violated"] is False
