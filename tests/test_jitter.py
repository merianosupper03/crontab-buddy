"""Tests for crontab_buddy.jitter."""

import pytest

from crontab_buddy.jitter import JitterResult, assess_jitter, batch_jitter, _field_jitter


def test_returns_jitter_result():
    result = assess_jitter("0 9 * * 1")
    assert isinstance(result, JitterResult)


def test_invalid_expression_has_error():
    result = assess_jitter("not a cron")
    assert result.error is not None
    assert result.label == "unknown"


def test_fixed_expression_score_is_zero():
    # All specific fields — no wildcards, no ranges, no steps
    result = assess_jitter("30 9 15 6 1")
    assert result.score == 0.0
    assert result.label == "fixed"
    assert result.fields_contributing == []


def test_every_minute_is_chaotic():
    result = assess_jitter("* * * * *")
    assert result.score > 0.8
    assert result.label == "chaotic"


def test_wildcard_contributes_to_jitter():
    result = assess_jitter("0 9 * * *")
    assert "dom" in result.fields_contributing
    assert "dow" in result.fields_contributing


def test_step_expression_has_jitter():
    result = assess_jitter("*/15 * * * *")
    assert result.score > 0.0
    assert "minute" in result.fields_contributing


def test_list_expression_contributes_jitter():
    result = assess_jitter("0,15,30,45 9 * * *")
    assert "minute" in result.fields_contributing


def test_range_expression_contributes_jitter():
    result = assess_jitter("0 8-10 * * *")
    assert "hour" in result.fields_contributing


def test_field_jitter_wildcard_is_one():
    assert _field_jitter("*") == 1.0


def test_field_jitter_plain_integer_is_zero():
    assert _field_jitter("5") == 0.0


def test_field_jitter_step_large_is_low():
    score = _field_jitter("*/30")
    assert 0.0 < score < 0.6


def test_field_jitter_step_one_is_high():
    score = _field_jitter("*/1")
    assert score > 0.9


def test_batch_jitter_returns_list():
    results = batch_jitter(["0 9 * * *", "* * * * *", "bad"])
    assert len(results) == 3


def test_batch_jitter_invalid_has_error():
    results = batch_jitter(["bad expression"])
    assert results[0].error is not None


def test_score_between_zero_and_one():
    for expr in ["*/5 * * * *", "0 12 * * 1-5", "15 3 1 1 *"]:
        r = assess_jitter(expr)
        if not r.error:
            assert 0.0 <= r.score <= 1.0


def test_str_representation_no_error():
    result = assess_jitter("0 9 * * 1")
    s = str(result)
    assert "JitterResult" in s
    assert "score" in s


def test_str_representation_with_error():
    result = assess_jitter("bad")
    s = str(result)
    assert "error" in s
