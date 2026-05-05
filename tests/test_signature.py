"""Tests for crontab_buddy.signature."""

import pytest
from crontab_buddy import signature as sig_mod


@pytest.fixture
def tmp_sig(tmp_path):
    return str(tmp_path / "sigs.json")


def test_compute_signature_is_16_chars():
    s = sig_mod.compute_signature("* * * * *")
    assert len(s) == 16


def test_compute_signature_deterministic():
    assert sig_mod.compute_signature("0 6 * * *") == sig_mod.compute_signature("0 6 * * *")


def test_compute_signature_differs_for_different_expressions():
    assert sig_mod.compute_signature("0 6 * * *") != sig_mod.compute_signature("0 7 * * *")


def test_save_and_get(tmp_sig):
    s = sig_mod.save_signature("0 6 * * *", label="morning", path=tmp_sig)
    entry = sig_mod.get_signature(s, path=tmp_sig)
    assert entry is not None
    assert entry["expression"] == "0 6 * * *"
    assert entry["label"] == "morning"


def test_get_missing_returns_none(tmp_sig):
    assert sig_mod.get_signature("nonexistent", path=tmp_sig) is None


def test_save_returns_signature_string(tmp_sig):
    s = sig_mod.save_signature("*/5 * * * *", path=tmp_sig)
    assert isinstance(s, str) and len(s) == 16


def test_verify_signature_true(tmp_sig):
    expr = "30 8 * * 1-5"
    s = sig_mod.compute_signature(expr)
    assert sig_mod.verify_signature(expr, s) is True


def test_verify_signature_false(tmp_sig):
    assert sig_mod.verify_signature("0 9 * * *", "0000000000000000") is False


def test_delete_existing(tmp_sig):
    s = sig_mod.save_signature("0 0 * * *", path=tmp_sig)
    assert sig_mod.delete_signature(s, path=tmp_sig) is True
    assert sig_mod.get_signature(s, path=tmp_sig) is None


def test_delete_missing_returns_false(tmp_sig):
    assert sig_mod.delete_signature("doesnotexist", path=tmp_sig) is False


def test_list_signatures_empty(tmp_sig):
    assert sig_mod.list_signatures(path=tmp_sig) == []


def test_list_signatures_returns_entries(tmp_sig):
    sig_mod.save_signature("* * * * *", label="every minute", path=tmp_sig)
    sig_mod.save_signature("0 12 * * *", label="noon", path=tmp_sig)
    entries = sig_mod.list_signatures(path=tmp_sig)
    assert len(entries) == 2
    assert all("sig" in e and "expression" in e for e in entries)


def test_save_no_label_stores_empty_string(tmp_sig):
    s = sig_mod.save_signature("0 1 * * *", path=tmp_sig)
    entry = sig_mod.get_signature(s, path=tmp_sig)
    assert entry["label"] == ""


def test_overwrite_signature_updates_label(tmp_sig):
    sig_mod.save_signature("0 6 * * *", label="old", path=tmp_sig)
    s = sig_mod.save_signature("0 6 * * *", label="new", path=tmp_sig)
    entry = sig_mod.get_signature(s, path=tmp_sig)
    assert entry["label"] == "new"
