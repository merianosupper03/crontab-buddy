"""Tests for crontab_buddy.tempo."""
import pytest
from crontab_buddy.tempo import (
    assess_tempo,
    batch_tempo,
    TempoResult,
    TEMPO_LEVELS,
    _level_and_score,
)


def test_returns_tempo_result():
    result = assess_tempo("* * * * *")
    assert isinstance(result, TempoResult)


def test_every_minute_is_frantic():
    result = assess_tempo("* * * * *")
    assert result.level == "frantic"


def test_every_minute_score_near_one():
    result = assess_tempo("* * * * *")
    assert result.score >= 0.9


def test_hourly_is_brisk_or_rapid():
    result = assess_tempo("0 * * * *")
    assert result.level in ("brisk", "rapid")


def test_daily_is_slow_or_moderate():
    result = assess_tempo("0 9 * * *")
    assert result.level in ("slow", "moderate", "glacial")


def test_weekly_is_glacial_or_slow():
    result = assess_tempo("0 9 * * 1")
    assert result.level in ("glacial", "slow")


def test_invalid_expression_returns_error():
    result = assess_tempo("not valid")
    assert result.error is not None
    assert result.level == "glacial"
    assert result.score == 0.0


def test_invalid_expression_interval_is_none():
    result = assess_tempo("bad expr")
    assert result.interval_seconds is None


def test_every_minute_interval_is_60():
    result = assess_tempo("* * * * *")
    assert result.interval_seconds == 60


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 * * * *", "0 0 * * *", "0 0 * * 0"]:
        r = assess_tempo(expr)
        assert 0.0 <= r.score <= 1.0


def test_level_in_known_levels():
    for expr in ["* * * * *", "0 * * * *", "0 0 * * *"]:
        r = assess_tempo(expr)
        assert r.level in TEMPO_LEVELS


def test_str_no_error():
    result = assess_tempo("0 * * * *")
    s = str(result)
    assert "TempoResult" in s
    assert "frantic" in s or "rapid" in s or "brisk" in s


def test_str_with_error():
    result = assess_tempo("bad")
    assert "error" in str(result).lower()


def test_batch_tempo_returns_list():
    results = batch_tempo(["* * * * *", "0 * * * *"])
    assert len(results) == 2
    assert all(isinstance(r, TempoResult) for r in results)


def test_level_and_score_60s_is_frantic():
    level, score = _level_and_score(60)
    assert level == "frantic"


def test_level_and_score_none_is_glacial():
    level, score = _level_and_score(None)
    assert level == "glacial"
    assert score == 0.0
