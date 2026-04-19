"""Tests for crontab_buddy.recap."""
import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path

from crontab_buddy.recap import recap, format_recap


def _make_history(tmp_path: Path, entries):
    p = tmp_path / "history.json"
    p.write_text(json.dumps(entries))
    return str(p)


def _ts(days_ago: int = 0) -> str:
    return (datetime.now() - timedelta(days=days_ago)).isoformat()


def test_recap_empty_history(tmp_path):
    path = _make_history(tmp_path, [])
    result = recap(days=7, path=path)
    assert result["total_uses"] == 0
    assert result["unique_expressions"] == 0
    assert result["top"] == []


def test_recap_counts_recent_entries(tmp_path):
    entries = [
        {"expression": "0 9 * * 1", "timestamp": _ts(0)},
        {"expression": "0 9 * * 1", "timestamp": _ts(1)},
        {"expression": "*/5 * * * *", "timestamp": _ts(2)},
    ]
    path = _make_history(tmp_path, entries)
    result = recap(days=7, path=path)
    assert result["total_uses"] == 3
    assert result["unique_expressions"] == 2


def test_recap_excludes_old_entries(tmp_path):
    entries = [
        {"expression": "0 9 * * 1", "timestamp": _ts(10)},
        {"expression": "*/5 * * * *", "timestamp": _ts(0)},
    ]
    path = _make_history(tmp_path, entries)
    result = recap(days=7, path=path)
    assert result["total_uses"] == 1
    assert result["top"][0]["expression"] == "*/5 * * * *"


def test_recap_top_sorted_by_frequency(tmp_path):
    entries = [
        {"expression": "0 0 * * *", "timestamp": _ts(0)},
        {"expression": "0 0 * * *", "timestamp": _ts(1)},
        {"expression": "0 0 * * *", "timestamp": _ts(2)},
        {"expression": "*/5 * * * *", "timestamp": _ts(0)},
    ]
    path = _make_history(tmp_path, entries)
    result = recap(days=7, path=path)
    assert result["top"][0]["expression"] == "0 0 * * *"
    assert result["top"][0]["count"] == 3


def test_recap_top_has_description(tmp_path):
    entries = [{"expression": "0 9 * * 1", "timestamp": _ts(0)}]
    path = _make_history(tmp_path, entries)
    result = recap(days=7, path=path)
    assert "description" in result["top"][0]
    assert result["top"][0]["description"] != ""


def test_format_recap_contains_key_info(tmp_path):
    entries = [{"expression": "0 9 * * 1", "timestamp": _ts(0)}]
    path = _make_history(tmp_path, entries)
    data = recap(days=7, path=path)
    text = format_recap(data)
    assert "Recap" in text
    assert "0 9 * * 1" in text
    assert "Total uses" in text


def test_format_recap_no_entries_message(tmp_path):
    path = _make_history(tmp_path, [])
    data = recap(days=7, path=path)
    text = format_recap(data)
    assert "No expressions" in text
