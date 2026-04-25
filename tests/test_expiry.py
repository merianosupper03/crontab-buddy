"""Tests for crontab_buddy.expiry."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta

import pytest

import crontab_buddy.expiry as expiry_mod


@pytest.fixture(autouse=True)
def tmp_expiry(tmp_path, monkeypatch):
    path = str(tmp_path / "expiry.json")
    monkeypatch.setattr(expiry_mod, "_FILE", path)
    yield path


EXPR = "0 9 * * 1"
_FUTURE = datetime(2099, 12, 31, 23, 59, 0)
_PAST = datetime(2000, 1, 1, 0, 0, 0)


def test_set_and_get(tmp_expiry):
    expiry_mod.set_expiry(EXPR, _FUTURE)
    entry = expiry_mod.get_expiry(EXPR)
    assert entry is not None
    assert entry["expires_at"] == _FUTURE.strftime(expiry_mod.DATE_FMT)


def test_get_missing_returns_none(tmp_expiry):
    assert expiry_mod.get_expiry("* * * * *") is None


def test_set_with_reason(tmp_expiry):
    expiry_mod.set_expiry(EXPR, _FUTURE, reason="project ended")
    entry = expiry_mod.get_expiry(EXPR)
    assert entry["reason"] == "project ended"


def test_overwrite_expiry(tmp_expiry):
    expiry_mod.set_expiry(EXPR, _FUTURE)
    new_dt = datetime(2088, 6, 15, 12, 0, 0)
    expiry_mod.set_expiry(EXPR, new_dt)
    entry = expiry_mod.get_expiry(EXPR)
    assert entry["expires_at"] == new_dt.strftime(expiry_mod.DATE_FMT)


def test_delete_existing(tmp_expiry):
    expiry_mod.set_expiry(EXPR, _FUTURE)
    result = expiry_mod.delete_expiry(EXPR)
    assert result is True
    assert expiry_mod.get_expiry(EXPR) is None


def test_delete_missing_returns_false(tmp_expiry):
    assert expiry_mod.delete_expiry("5 5 * * *") is False


def test_is_expired_past(tmp_expiry):
    expiry_mod.set_expiry(EXPR, _PAST)
    assert expiry_mod.is_expired(EXPR) is True


def test_is_expired_future(tmp_expiry):
    expiry_mod.set_expiry(EXPR, _FUTURE)
    assert expiry_mod.is_expired(EXPR) is False


def test_is_expired_no_entry(tmp_expiry):
    assert expiry_mod.is_expired("1 2 3 4 5") is False


def test_is_expired_custom_now(tmp_expiry):
    pivot = datetime(2050, 6, 1, 12, 0, 0)
    expiry_mod.set_expiry(EXPR, pivot)
    before = pivot - timedelta(seconds=1)
    after = pivot + timedelta(seconds=1)
    assert expiry_mod.is_expired(EXPR, now=before) is False
    assert expiry_mod.is_expired(EXPR, now=after) is True


def test_list_expiries(tmp_expiry):
    expiry_mod.set_expiry(EXPR, _FUTURE, reason="test")
    expiry_mod.set_expiry("*/5 * * * *", _PAST)
    entries = expiry_mod.list_expiries()
    assert len(entries) == 2
    exprs = {e["expression"] for e in entries}
    assert EXPR in exprs
    assert "*/5 * * * *" in exprs


def test_list_expiries_empty(tmp_expiry):
    assert expiry_mod.list_expiries() == []
