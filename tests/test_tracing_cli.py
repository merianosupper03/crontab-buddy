"""Tests for crontab_buddy.tracing_cli."""

import pytest
from crontab_buddy import tracing
from crontab_buddy import tracing_cli


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def tp(tmp_path):
    return str(tmp_path / "traces.json")


def test_cmd_trace_start_prints(tp, capsys):
    args = Args(expression="* * * * *", label=None)
    tracing_cli.cmd_trace_start(args, path=tp)
    out = capsys.readouterr().out
    assert "Trace started" in out
    assert "* * * * *" in out


def test_cmd_trace_start_with_label_prints_label(tp, capsys):
    args = Args(expression="0 0 * * *", label="midnight")
    tracing_cli.cmd_trace_start(args, path=tp)
    out = capsys.readouterr().out
    assert "midnight" in out


def test_cmd_trace_finish_success(tp, capsys):
    tid = tracing.start_trace("0 6 * * *", path=tp)
    args = Args(expression="0 6 * * *", trace_id=tid, status="ok")
    tracing_cli.cmd_trace_finish(args, path=tp)
    out = capsys.readouterr().out
    assert "finished" in out
    assert "ok" in out


def test_cmd_trace_finish_invalid_status_prints_error(tp, capsys):
    tid = tracing.start_trace("* * * * *", path=tp)
    args = Args(expression="* * * * *", trace_id=tid, status="bad")
    tracing_cli.cmd_trace_finish(args, path=tp)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_trace_finish_not_found_prints_message(tp, capsys):
    args = Args(expression="* * * * *", trace_id="nope", status="ok")
    tracing_cli.cmd_trace_finish(args, path=tp)
    out = capsys.readouterr().out
    assert "No running trace" in out


def test_cmd_trace_list_no_traces(tp, capsys):
    args = Args(expression="0 0 * * *")
    tracing_cli.cmd_trace_list(args, path=tp)
    out = capsys.readouterr().out
    assert "No traces" in out


def test_cmd_trace_list_shows_spans(tp, capsys):
    tracing.start_trace("*/10 * * * *", path=tp)
    args = Args(expression="*/10 * * * *")
    tracing_cli.cmd_trace_list(args, path=tp)
    out = capsys.readouterr().out
    assert "running" in out


def test_cmd_trace_clear_prints_cleared(tp, capsys):
    tracing.start_trace("0 12 * * *", path=tp)
    args = Args(expression="0 12 * * *")
    tracing_cli.cmd_trace_clear(args, path=tp)
    out = capsys.readouterr().out
    assert "cleared" in out


def test_cmd_trace_list_all_empty(tp, capsys):
    args = Args()
    tracing_cli.cmd_trace_list_all(args, path=tp)
    out = capsys.readouterr().out
    assert "No traced" in out


def test_cmd_trace_list_all_shows_expressions(tp, capsys):
    tracing.start_trace("* * * * *", path=tp)
    tracing.start_trace("0 0 * * 0", path=tp)
    args = Args()
    tracing_cli.cmd_trace_list_all(args, path=tp)
    out = capsys.readouterr().out
    assert "* * * * *" in out
    assert "0 0 * * 0" in out
