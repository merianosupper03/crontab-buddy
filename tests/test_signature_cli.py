"""Tests for crontab_buddy.signature_cli."""

import pytest
from unittest.mock import patch
from crontab_buddy import signature as sig_mod
from crontab_buddy import signature_cli as cli


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def tp(tmp_path):
    p = str(tmp_path / "sigs.json")
    with patch.object(sig_mod, "_DEFAULT_PATH", p):
        yield p


def test_cmd_compute_prints_signature(tp, capsys):
    cli.cmd_signature_compute(Args(expression="* * * * *"))
    out = capsys.readouterr().out
    assert "Signature:" in out


def test_cmd_save_prints_saved(tp, capsys):
    cli.cmd_signature_save(Args(expression="0 6 * * *", label="dawn"))
    out = capsys.readouterr().out
    assert "Saved signature:" in out


def test_cmd_get_existing(tp, capsys):
    s = sig_mod.save_signature("0 8 * * *", label="morning", path=tp)
    cli.cmd_signature_get(Args(sig=s))
    out = capsys.readouterr().out
    assert "0 8 * * *" in out
    assert "morning" in out


def test_cmd_get_missing(tp, capsys):
    cli.cmd_signature_get(Args(sig="0000000000000000"))
    out = capsys.readouterr().out
    assert "No entry found" in out


def test_cmd_verify_match(tp, capsys):
    from crontab_buddy.signature import compute_signature
    expr = "0 12 * * *"
    s = compute_signature(expr)
    cli.cmd_signature_verify(Args(expression=expr, sig=s))
    out = capsys.readouterr().out
    assert "OK" in out


def test_cmd_verify_mismatch(tp, capsys):
    cli.cmd_signature_verify(Args(expression="0 12 * * *", sig="0000000000000000"))
    out = capsys.readouterr().out
    assert "MISMATCH" in out


def test_cmd_delete_success(tp, capsys):
    s = sig_mod.save_signature("*/10 * * * *", path=tp)
    cli.cmd_signature_delete(Args(sig=s))
    out = capsys.readouterr().out
    assert "Deleted" in out


def test_cmd_delete_missing(tp, capsys):
    cli.cmd_signature_delete(Args(sig="nope"))
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_list_empty(tp, capsys):
    cli.cmd_signature_list(Args())
    out = capsys.readouterr().out
    assert "No signatures" in out


def test_cmd_list_shows_entries(tp, capsys):
    sig_mod.save_signature("0 0 * * *", label="midnight", path=tp)
    cli.cmd_signature_list(Args())
    out = capsys.readouterr().out
    assert "0 0 * * *" in out
    assert "midnight" in out
