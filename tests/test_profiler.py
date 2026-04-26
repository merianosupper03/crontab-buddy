"""Tests for crontab_buddy/profiler.py"""

import pytest

from crontab_buddy.profiler import (
    delete_profile,
    get_profile,
    list_profiles,
    set_profile,
)


@pytest.fixture
def tmp_profiler(tmp_path):
    return str(tmp_path / "profiler.json")


def test_set_and_get(tmp_profiler):
    set_profile("0 * * * *", avg_seconds=5.0, path=tmp_profiler)
    result = get_profile("0 * * * *", path=tmp_profiler)
    assert result is not None
    assert result["avg_seconds"] == 5.0


def test_get_missing_returns_none(tmp_profiler):
    assert get_profile("* * * * *", path=tmp_profiler) is None


def test_overwrite_profile(tmp_profiler):
    set_profile("0 * * * *", avg_seconds=3.0, path=tmp_profiler)
    set_profile("0 * * * *", avg_seconds=7.5, path=tmp_profiler)
    result = get_profile("0 * * * *", path=tmp_profiler)
    assert result["avg_seconds"] == 7.5


def test_max_seconds_stored(tmp_profiler):
    set_profile("0 0 * * *", avg_seconds=10.0, max_seconds=30.0, path=tmp_profiler)
    result = get_profile("0 0 * * *", path=tmp_profiler)
    assert result["max_seconds"] == 30.0


def test_notes_stored(tmp_profiler):
    set_profile("*/5 * * * *", avg_seconds=2.0, notes="fast job", path=tmp_profiler)
    result = get_profile("*/5 * * * *", path=tmp_profiler)
    assert result["notes"] == "fast job"


def test_invalid_avg_seconds_raises(tmp_profiler):
    with pytest.raises(ValueError, match="avg_seconds"):
        set_profile("* * * * *", avg_seconds=-1.0, path=tmp_profiler)


def test_max_less_than_avg_raises(tmp_profiler):
    with pytest.raises(ValueError, match="max_seconds"):
        set_profile("* * * * *", avg_seconds=10.0, max_seconds=5.0, path=tmp_profiler)


def test_delete_existing(tmp_profiler):
    set_profile("0 12 * * *", avg_seconds=1.0, path=tmp_profiler)
    assert delete_profile("0 12 * * *", path=tmp_profiler) is True
    assert get_profile("0 12 * * *", path=tmp_profiler) is None


def test_delete_missing_returns_false(tmp_profiler):
    assert delete_profile("0 12 * * *", path=tmp_profiler) is False


def test_list_profiles_returns_all(tmp_profiler):
    set_profile("0 * * * *", avg_seconds=5.0, path=tmp_profiler)
    set_profile("*/10 * * * *", avg_seconds=2.0, path=tmp_profiler)
    results = list_profiles(path=tmp_profiler)
    assert len(results) == 2
    expressions = [r["expression"] for r in results]
    assert "0 * * * *" in expressions
    assert "*/10 * * * *" in expressions


def test_list_profiles_has_description(tmp_profiler):
    set_profile("0 9 * * 1", avg_seconds=4.0, path=tmp_profiler)
    results = list_profiles(path=tmp_profiler)
    assert results[0]["description"] != ""
    assert "invalid" not in results[0]["description"]


def test_list_profiles_invalid_expression(tmp_profiler):
    import json
    # manually inject a bad expression
    with open(tmp_profiler, "w") as f:
        json.dump({"bad expr": {"avg_seconds": 1.0, "max_seconds": None, "notes": ""}}, f)
    results = list_profiles(path=tmp_profiler)
    assert results[0]["description"] == "(invalid expression)"
