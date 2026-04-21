"""Tests for crontab_buddy.quota_cli."""

import pytest
from unittest.mock import patch

from crontab_buddy.quota_cli import (
    cmd_quota_set,
    cmd_quota_get,
    cmd_quota_delete,
    cmd_quota_list,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def tp(tmp_path, monkeypatch):
    quota_file = tmp_path / "quota.json"
    monkeypatch.setattr("crontab_buddy.quota._QUOTA_FILE", str(quota_file))
    return quota_file


def test_cmd_set_prints(tp, capsys):
    args = Args(expression="0 9 * * 1", max_runs=5, period="weekly")
    cmd_quota_set(args)
    out = capsys.readouterr().out
    assert "0 9 * * 1" in out
    assert "5" in out
    assert "weekly" in out


def test_cmd_set_invalid_max_runs_prints_error(tp, capsys):
    args = Args(expression="0 9 * * 1", max_runs=0, period="daily")
    cmd_quota_set(args)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_set_invalid_period_prints_error(tp, capsys):
    args = Args(expression="0 9 * * 1", max_runs=3, period="never")
    cmd_quota_set(args)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_get_existing(tp, capsys):
    set_args = Args(expression="*/10 * * * *", max_runs=6, period="hourly")
    cmd_quota_set(set_args)
    get_args = Args(expression="*/10 * * * *")
    cmd_quota_get(get_args)
    out = capsys.readouterr().out
    assert "6" in out
    assert "hourly" in out


def test_cmd_get_missing(tp, capsys):
    args = Args(expression="1 2 3 4 5")
    cmd_quota_get(args)
    out = capsys.readouterr().out
    assert "No quota" in out


def test_cmd_delete_success(tp, capsys):
    set_args = Args(expression="0 0 * * *", max_runs=1, period="daily")
    cmd_quota_set(set_args)
    del_args = Args(expression="0 0 * * *")
    cmd_quota_delete(del_args)
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_delete_missing(tp, capsys):
    args = Args(expression="9 9 9 9 *")
    cmd_quota_delete(args)
    out = capsys.readouterr().out
    assert "No quota found" in out


def test_cmd_list_empty(tp, capsys):
    cmd_quota_list(Args())
    out = capsys.readouterr().out
    assert "No quotas" in out


def test_cmd_list_shows_entries(tp, capsys):
    cmd_quota_set(Args(expression="0 * * * *", max_runs=4, period="daily"))
    cmd_quota_set(Args(expression="*/5 * * * *", max_runs=2, period="hourly"))
    capsys.readouterr()
    cmd_quota_list(Args())
    out = capsys.readouterr().out
    assert "0 * * * *" in out
    assert "*/5 * * * *" in out
