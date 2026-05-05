"""Tests for crontab_buddy.heartbeat."""
import time
import pytest

from crontab_buddy.heartbeat import (
    clear_heartbeats,
    get_heartbeats,
    latest_heartbeat,
    list_heartbeats,
    record_heartbeat,
)

EXPR = "0 9 * * 1"


@pytest.fixture
def tmp_hb(tmp_path):
    return tmp_path / "heartbeats.json"


def test_record_and_get(tmp_hb):
    record_heartbeat(EXPR, path=tmp_hb)
    records = get_heartbeats(EXPR, path=tmp_hb)
    assert len(records) == 1
    assert records[0]["status"] == "ok"


def test_default_status_is_ok(tmp_hb):
    record_heartbeat(EXPR, path=tmp_hb)
    rec = latest_heartbeat(EXPR, path=tmp_hb)
    assert rec["status"] == "ok"


def test_warn_status_stored(tmp_hb):
    record_heartbeat(EXPR, status="warn", path=tmp_hb)
    rec = latest_heartbeat(EXPR, path=tmp_hb)
    assert rec["status"] == "warn"


def test_fail_status_stored(tmp_hb):
    record_heartbeat(EXPR, status="fail", path=tmp_hb)
    rec = latest_heartbeat(EXPR, path=tmp_hb)
    assert rec["status"] == "fail"


def test_invalid_status_raises(tmp_hb):
    with pytest.raises(ValueError):
        record_heartbeat(EXPR, status="unknown", path=tmp_hb)


def test_multiple_records_newest_first(tmp_hb):
    record_heartbeat(EXPR, status="ok", path=tmp_hb)
    time.sleep(0.01)
    record_heartbeat(EXPR, status="fail", path=tmp_hb)
    records = get_heartbeats(EXPR, path=tmp_hb)
    assert records[0]["status"] == "fail"


def test_get_missing_returns_empty(tmp_hb):
    records = get_heartbeats("* * * * *", path=tmp_hb)
    assert records == []


def test_latest_missing_returns_none(tmp_hb):
    assert latest_heartbeat("* * * * *", path=tmp_hb) is None


def test_clear_existing(tmp_hb):
    record_heartbeat(EXPR, path=tmp_hb)
    result = clear_heartbeats(EXPR, path=tmp_hb)
    assert result is True
    assert get_heartbeats(EXPR, path=tmp_hb) == []


def test_clear_missing_returns_false(tmp_hb):
    assert clear_heartbeats("* * * * *", path=tmp_hb) is False


def test_list_all(tmp_hb):
    record_heartbeat(EXPR, path=tmp_hb)
    record_heartbeat("*/5 * * * *", status="warn", path=tmp_hb)
    data = list_heartbeats(path=tmp_hb)
    assert EXPR in data
    assert "*/5 * * * *" in data


def test_timestamp_is_recent(tmp_hb):
    before = time.time()
    record_heartbeat(EXPR, path=tmp_hb)
    after = time.time()
    rec = latest_heartbeat(EXPR, path=tmp_hb)
    assert before <= rec["timestamp"] <= after
