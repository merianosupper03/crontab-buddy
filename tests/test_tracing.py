"""Tests for crontab_buddy.tracing."""

import pytest
from crontab_buddy import tracing


@pytest.fixture
def tmp_trace(tmp_path):
    return str(tmp_path / "traces.json")


def test_start_trace_returns_id(tmp_trace):
    tid = tracing.start_trace("* * * * *", path=tmp_trace)
    assert isinstance(tid, str)
    assert len(tid) == 12


def test_start_trace_status_is_running(tmp_trace):
    tid = tracing.start_trace("0 * * * *", path=tmp_trace)
    spans = tracing.get_traces("0 * * * *", path=tmp_trace)
    assert spans[0]["status"] == "running"
    assert spans[0]["trace_id"] == tid


def test_finish_trace_sets_status(tmp_trace):
    tid = tracing.start_trace("0 0 * * *", path=tmp_trace)
    result = tracing.finish_trace("0 0 * * *", tid, status="ok", path=tmp_trace)
    assert result is True
    spans = tracing.get_traces("0 0 * * *", path=tmp_trace)
    assert spans[0]["status"] == "ok"


def test_finish_trace_records_duration(tmp_trace):
    tid = tracing.start_trace("5 4 * * *", path=tmp_trace)
    tracing.finish_trace("5 4 * * *", tid, path=tmp_trace)
    spans = tracing.get_traces("5 4 * * *", path=tmp_trace)
    assert spans[0]["duration_ms"] is not None
    assert spans[0]["duration_ms"] >= 0


def test_finish_trace_invalid_status_raises(tmp_trace):
    tid = tracing.start_trace("* * * * *", path=tmp_trace)
    with pytest.raises(ValueError):
        tracing.finish_trace("* * * * *", tid, status="bad", path=tmp_trace)


def test_finish_trace_unknown_id_returns_false(tmp_trace):
    tracing.start_trace("* * * * *", path=tmp_trace)
    result = tracing.finish_trace("* * * * *", "nonexistent", path=tmp_trace)
    assert result is False


def test_start_trace_with_label(tmp_trace):
    tracing.start_trace("0 12 * * *", label="noon-job", path=tmp_trace)
    spans = tracing.get_traces("0 12 * * *", path=tmp_trace)
    assert spans[0]["label"] == "noon-job"


def test_multiple_traces_newest_first(tmp_trace):
    tracing.start_trace("0 6 * * *", path=tmp_trace)
    tid2 = tracing.start_trace("0 6 * * *", path=tmp_trace)
    spans = tracing.get_traces("0 6 * * *", path=tmp_trace)
    assert spans[0]["trace_id"] == tid2


def test_clear_traces_removes_all(tmp_trace):
    tracing.start_trace("*/5 * * * *", path=tmp_trace)
    tracing.clear_traces("*/5 * * * *", path=tmp_trace)
    assert tracing.get_traces("*/5 * * * *", path=tmp_trace) == []


def test_list_traced_expressions(tmp_trace):
    tracing.start_trace("* * * * *", path=tmp_trace)
    tracing.start_trace("0 0 * * 0", path=tmp_trace)
    exprs = tracing.list_traced_expressions(path=tmp_trace)
    assert "* * * * *" in exprs
    assert "0 0 * * 0" in exprs


def test_fail_status_stored(tmp_trace):
    tid = tracing.start_trace("0 3 * * *", path=tmp_trace)
    tracing.finish_trace("0 3 * * *", tid, status="fail", path=tmp_trace)
    spans = tracing.get_traces("0 3 * * *", path=tmp_trace)
    assert spans[0]["status"] == "fail"
