"""Tests for crontab_buddy.contention."""

import pytest
from crontab_buddy.contention import assess_contention, ContentionResult


def test_returns_contention_result():
    r = assess_contention("* * * * *", "0 * * * *")
    assert isinstance(r, ContentionResult)


def test_identical_expressions_full_contention():
    r = assess_contention("0 9 * * *", "0 9 * * *")
    assert r.score == 1.0
    assert r.grade == "critical"


def test_no_overlap_different_hours():
    r = assess_contention("0 8 * * *", "0 9 * * *")
    assert r.overlap_minutes == 0
    assert r.score == 0.0
    assert r.grade == "none"


def test_partial_overlap_hourly_vs_specific():
    # "0 * * * *" fires at minute 0 every hour (24 times)
    # "0 9 * * *" fires once at 09:00
    r = assess_contention("0 * * * *", "0 9 * * *")
    assert r.overlap_minutes == 1
    assert r.score > 0.0
    assert r.grade in ("low", "moderate", "high", "critical")


def test_every_minute_vs_every_minute_is_critical():
    r = assess_contention("* * * * *", "* * * * *")
    assert r.score == 1.0
    assert r.grade == "critical"


def test_invalid_expr_a_returns_error():
    r = assess_contention("bad expr", "0 9 * * *")
    assert r.error is not None
    assert r.score == 0.0


def test_invalid_expr_b_returns_error():
    r = assess_contention("0 9 * * *", "not valid")
    assert r.error is not None


def test_overlap_minutes_is_non_negative():
    r = assess_contention("*/15 * * * *", "*/30 * * * *")
    assert r.overlap_minutes >= 0


def test_str_contains_grade():
    r = assess_contention("0 9 * * *", "0 10 * * *")
    assert "none" in str(r)


def test_str_contains_error_when_invalid():
    r = assess_contention("bad", "0 9 * * *")
    assert "error" in str(r)


def test_score_between_zero_and_one():
    for expr_a, expr_b in [
        ("*/5 * * * *", "*/7 * * * *"),
        ("0 0 * * *", "0 12 * * *"),
        ("* * * * *", "0 0 * * *"),
    ]:
        r = assess_contention(expr_a, expr_b)
        assert 0.0 <= r.score <= 1.0


def test_list_field_overlap():
    r = assess_contention("0,30 9 * * *", "0 9 * * *")
    assert r.overlap_minutes == 1
