"""Tests for crontab_buddy.runlog and runlog_cli."""

import pytest
from unittest.mock import MagicMock
from crontab_buddy import runlog, runlog_cli


@pytest.fixture
def tmp_runlog(tmp_path):
    return str(tmp_path / "runlog.json")


def test_log_and_retrieve(tmp_runlog):
    runlog.log_run("* * * * *", "ok", path=tmp_runlog)
    entries = runlog.get_runs("* * * * *", path=tmp_runlog)
    assert len(entries) == 1
    assert entries[0]["status"] == "ok"


def test_log_fail_status(tmp_runlog):
    runlog.log_run("0 * * * *", "fail", message="timeout", path=tmp_runlog)
    entries = runlog.get_runs("0 * * * *", path=tmp_runlog)
    assert entries[0]["status"] == "fail"
    assert entries[0]["message"] == "timeout"


def test_invalid_status_raises(tmp_runlog):
    with pytest.raises(ValueError):
        runlog.log_run("* * * * *", "unknown", path=tmp_runlog)


def test_multiple_runs_newest_first(tmp_runlog):
    runlog.log_run("5 4 * * *", "ok", message="first", path=tmp_runlog)
    runlog.log_run("5 4 * * *", "fail", message="second", path=tmp_runlog)
    entries = runlog.get_runs("5 4 * * *", path=tmp_runlog)
    assert entries[0]["message"] == "second"
    assert entries[1]["message"] == "first"


def test_get_runs_limit(tmp_runlog):
    for i in range(5):
        runlog.log_run("* * * * *", "ok", message=str(i), path=tmp_runlog)
    entries = runlog.get_runs("* * * * *", path=tmp_runlog, limit=2)
    assert len(entries) == 2


def test_get_runs_missing_expression(tmp_runlog):
    entries = runlog.get_runs("1 2 3 4 5", path=tmp_runlog)
    assert entries == []


def test_clear_runs(tmp_runlog):
    runlog.log_run("* * * * *", "ok", path=tmp_runlog)
    runlog.clear_runs("* * * * *", path=tmp_runlog)
    assert runlog.get_runs("* * * * *", path=tmp_runlog) == []


def test_list_all_runs(tmp_runlog):
    runlog.log_run("* * * * *", "ok", path=tmp_runlog)
    runlog.log_run("0 0 * * *", "fail", path=tmp_runlog)
    all_runs = runlog.list_all_runs(path=tmp_runlog)
    assert "* * * * *" in all_runs
    assert "0 0 * * *" in all_runs


def test_cmd_runlog_add_prints(tmp_runlog, capsys):
    args = MagicMock(expression="* * * * *", status="ok", message="done")
    runlog_cli.cmd_runlog_add(args, path=tmp_runlog)
    out = capsys.readouterr().out
    assert "Logged ok" in out


def test_cmd_runlog_add_invalid_status_prints_error(tmp_runlog, capsys):
    args = MagicMock(expression="* * * * *", status="bad", message="")
    runlog_cli.cmd_runlog_add(args, path=tmp_runlog)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_runlog_get_prints_entries(tmp_runlog, capsys):
    runlog.log_run("* * * * *", "ok", message="ran", path=tmp_runlog)
    args = MagicMock(expression="* * * * *", limit=None)
    runlog_cli.cmd_runlog_get(args, path=tmp_runlog)
    out = capsys.readouterr().out
    assert "OK" in out


def test_cmd_runlog_get_empty(tmp_runlog, capsys):
    args = MagicMock(expression="1 2 3 4 5", limit=None)
    runlog_cli.cmd_runlog_get(args, path=tmp_runlog)
    out = capsys.readouterr().out
    assert "No run log" in out


def test_cmd_runlog_clear_prints(tmp_runlog, capsys):
    runlog.log_run("* * * * *", "ok", path=tmp_runlog)
    args = MagicMock(expression="* * * * *")
    runlog_cli.cmd_runlog_clear(args, path=tmp_runlog)
    out = capsys.readouterr().out
    assert "Cleared" in out


def test_cmd_runlog_list_empty(tmp_runlog, capsys):
    args = MagicMock()
    runlog_cli.cmd_runlog_list(args, path=tmp_runlog)
    out = capsys.readouterr().out
    assert "empty" in out
