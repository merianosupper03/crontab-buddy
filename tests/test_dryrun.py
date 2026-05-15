"""Tests for crontab_buddy.dryrun."""

from datetime import datetime, timezone
import pytest

from crontab_buddy.dryrun import dry_run, format_dry_run_json


def _utc(year, month, day, hour, minute):
    return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)


def test_dry_run_returns_result():
    result = dry_run("* * * * *")
    assert result is not None


def test_invalid_expression_has_error():
    result = dry_run("invalid")
    assert result.error is not None
    assert result.would_fire_now is False
    assert result.next_occurrence is None


def test_every_minute_would_fire_now():
    at = _utc(2024, 6, 15, 12, 30)
    result = dry_run("* * * * *", at=at)
    assert result.would_fire_now is True
    assert result.error is None


def test_specific_time_fires_at_matching_moment():
    at = _utc(2024, 6, 15, 9, 0)
    result = dry_run("0 9 * * *", at=at)
    assert result.would_fire_now is True


def test_specific_time_does_not_fire_at_wrong_moment():
    at = _utc(2024, 6, 15, 9, 1)
    result = dry_run("0 9 * * *", at=at)
    assert result.would_fire_now is False


def test_next_occurrence_is_populated():
    at = _utc(2024, 6, 15, 12, 0)
    result = dry_run("0 13 * * *", at=at)
    assert result.next_occurrence is not None
    assert result.next_occurrence > at


def test_description_is_non_empty():
    result = dry_run("0 9 * * 1")
    assert isinstance(result.description, str)
    assert len(result.description) > 0


def test_str_contains_expression():
    result = dry_run("30 6 * * *")
    text = str(result)
    assert "30 6 * * *" in text


def test_str_error_shows_error_label():
    result = dry_run("bad expr here")
    assert "[error]" in str(result)


def test_format_dry_run_json_keys():
    result = dry_run("* * * * *")
    d = format_dry_run_json(result)
    assert "expression" in d
    assert "description" in d
    assert "would_fire_now" in d
    assert "next_occurrence" in d
    assert "error" in d


def test_format_dry_run_json_error_expression():
    result = dry_run("not valid")
    d = format_dry_run_json(result)
    assert d["error"] is not None
    assert d["next_occurrence"] is None


def test_format_dry_run_json_next_occurrence_is_iso_string():
    at = _utc(2024, 1, 1, 0, 0)
    result = dry_run("* * * * *", at=at)
    d = format_dry_run_json(result)
    if d["next_occurrence"] is not None:
        assert "T" in d["next_occurrence"] or " " in d["next_occurrence"]
