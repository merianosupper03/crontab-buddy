"""Tests for crontab_buddy.digest."""
import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from crontab_buddy.digest import build_digest, format_digest


def _ts(days_ago: int = 0) -> str:
    return (datetime.utcnow() - timedelta(days=days_ago)).isoformat()


def _write_history(path: Path, entries: list) -> None:
    path.write_text(json.dumps(entries))


@pytest.fixture
def tmp_hist(tmp_path):
    return tmp_path / "history.json"


def test_digest_empty_history(tmp_hist):
    _write_history(tmp_hist, [])
    result = build_digest(days=7, path=str(tmp_hist))
    assert result["total_uses"] == 0
    assert result["unique_expressions"] == 0
    assert result["top_expressions"] == []


def test_digest_counts_recent(tmp_hist):
    entries = [
        {"expression": "0 9 * * 1", "timestamp": _ts(0)},
        {"expression": "0 9 * * 1", "timestamp": _ts(1)},
        {"expression": "*/5 * * * *", "timestamp": _ts(2)},
    ]
    _write_history(tmp_hist, entries)
    result = build_digest(days=7, path=str(tmp_hist))
    assert result["total_uses"] == 3
    assert result["unique_expressions"] == 2


def test_digest_excludes_old_entries(tmp_hist):
    entries = [
        {"expression": "0 9 * * 1", "timestamp": _ts(0)},
        {"expression": "0 9 * * 1", "timestamp": _ts(10)},  # outside 7-day window
    ]
    _write_history(tmp_hist, entries)
    result = build_digest(days=7, path=str(tmp_hist))
    assert result["total_uses"] == 1


def test_digest_top_expressions_sorted(tmp_hist):
    entries = [
        {"expression": "*/5 * * * *", "timestamp": _ts(0)},
        {"expression": "*/5 * * * *", "timestamp": _ts(1)},
        {"expression": "0 9 * * 1", "timestamp": _ts(2)},
    ]
    _write_history(tmp_hist, entries)
    result = build_digest(days=7, path=str(tmp_hist))
    assert result["top_expressions"][0]["expression"] == "*/5 * * * *"
    assert result["top_expressions"][0]["count"] == 2


def test_digest_top_expressions_have_description(tmp_hist):
    entries = [{"expression": "0 9 * * 1", "timestamp": _ts(0)}]
    _write_history(tmp_hist, entries)
    result = build_digest(days=7, path=str(tmp_hist))
    assert "description" in result["top_expressions"][0]
    assert result["top_expressions"][0]["description"] != ""


def test_format_digest_contains_period(tmp_hist):
    _write_history(tmp_hist, [])
    digest = build_digest(days=7, path=str(tmp_hist))
    text = format_digest(digest)
    assert "7" in text
    assert "Digest" in text


def test_format_digest_lists_top_expr(tmp_hist):
    entries = [{"expression": "0 9 * * 1", "timestamp": _ts(0)}]
    _write_history(tmp_hist, entries)
    digest = build_digest(days=7, path=str(tmp_hist))
    text = format_digest(digest)
    assert "0 9 * * 1" in text
