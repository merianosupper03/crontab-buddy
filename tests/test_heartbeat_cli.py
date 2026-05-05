"""Tests for crontab_buddy.heartbeat_cli."""
import pytest
from unittest.mock import patch

from crontab_buddy.heartbeat_cli import (
    cmd_heartbeat_ping,
    cmd_heartbeat_get,
    cmd_heartbeat_latest,
    cmd_heartbeat_clear,
    cmd_heartbeat_list,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def tp(tmp_path):
    hb_file = tmp_path / "heartbeats.json"
    with patch("crontab_buddy.heartbeat._DEFAULT_PATH", hb_file):
        with patch("crontab_buddy.heartbeat_cli.record_heartbeat",
                   wraps=lambda *a, **kw: __import__(
                       "crontab_buddy.heartbeat", fromlist=["record_heartbeat"]
                   ).record_heartbeat(*a, path=hb_file, **{k: v for k, v in kw.items() if k != "path"})):
            yield hb_file


def _ping(expr, status="ok", path=None):
    from crontab_buddy.heartbeat import record_heartbeat
    record_heartbeat(expr, status=status, path=path)


def test_cmd_ping_prints(tmp_path, capsys):
    hb = tmp_path / "hb.json"
    with patch("crontab_buddy.heartbeat_cli.record_heartbeat") as mock_rec:
        cmd_heartbeat_ping(Args(expression="0 9 * * 1", status="ok"))
        mock_rec.assert_called_once()
    out = capsys.readouterr().out
    assert "Heartbeat recorded" in out


def test_cmd_ping_invalid_status_prints_error(tmp_path, capsys):
    with patch("crontab_buddy.heartbeat_cli.record_heartbeat",
               side_effect=ValueError("bad status")):
        cmd_heartbeat_ping(Args(expression="0 9 * * 1", status="bad"))
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_get_no_records(tmp_path, capsys):
    hb = tmp_path / "hb.json"
    with patch("crontab_buddy.heartbeat_cli.get_heartbeats", return_value=[]):
        cmd_heartbeat_get(Args(expression="0 9 * * 1"))
    out = capsys.readouterr().out
    assert "No heartbeats" in out


def test_cmd_get_with_records(tmp_path, capsys):
    import time
    records = [{"timestamp": time.time(), "status": "ok"}]
    with patch("crontab_buddy.heartbeat_cli.get_heartbeats", return_value=records):
        cmd_heartbeat_get(Args(expression="0 9 * * 1"))
    out = capsys.readouterr().out
    assert "OK" in out


def test_cmd_latest_none(tmp_path, capsys):
    with patch("crontab_buddy.heartbeat_cli.latest_heartbeat", return_value=None):
        cmd_heartbeat_latest(Args(expression="0 9 * * 1"))
    out = capsys.readouterr().out
    assert "No heartbeats" in out


def test_cmd_clear_success(tmp_path, capsys):
    with patch("crontab_buddy.heartbeat_cli.clear_heartbeats", return_value=True):
        cmd_heartbeat_clear(Args(expression="0 9 * * 1"))
    out = capsys.readouterr().out
    assert "Cleared" in out


def test_cmd_clear_missing(tmp_path, capsys):
    with patch("crontab_buddy.heartbeat_cli.clear_heartbeats", return_value=False):
        cmd_heartbeat_clear(Args(expression="0 9 * * 1"))
    out = capsys.readouterr().out
    assert "No heartbeats" in out


def test_cmd_list_empty(tmp_path, capsys):
    with patch("crontab_buddy.heartbeat_cli.list_heartbeats", return_value={}):
        cmd_heartbeat_list(Args())
    out = capsys.readouterr().out
    assert "No heartbeat records" in out
