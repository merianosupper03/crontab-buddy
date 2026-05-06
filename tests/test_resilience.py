"""Tests for crontab_buddy.resilience."""

import pytest
from crontab_buddy.resilience import score_resilience, ResilienceResult, _grade


EXPR = "0 * * * *"


def test_baseline_score_no_flags():
    r = score_resilience(EXPR)
    assert r.score == 20
    assert r.grade == "D"


def test_all_flags_gives_high_score():
    r = score_resilience(
        EXPR,
        has_retry=True,
        has_healthcheck=True,
        has_timeout=True,
        has_lock=True,
        has_notify=True,
    )
    assert r.score == 100
    assert r.grade == "A"


def test_retry_adds_score():
    r = score_resilience(EXPR, has_retry=True)
    assert r.score == 40


def test_healthcheck_adds_score():
    r = score_resilience(EXPR, has_healthcheck=True)
    assert r.score == 40


def test_timeout_adds_score():
    r = score_resilience(EXPR, has_timeout=True)
    assert r.score == 35


def test_lock_adds_score():
    r = score_resilience(EXPR, has_lock=True)
    assert r.score == 35


def test_notify_adds_score():
    r = score_resilience(EXPR, has_notify=True)
    assert r.score == 30


def test_high_frequency_penalty():
    r_no_penalty = score_resilience(EXPR, has_retry=True, is_high_frequency=False)
    r_penalty = score_resilience(EXPR, has_retry=True, is_high_frequency=True)
    assert r_penalty.score == r_no_penalty.score - 10


def test_score_capped_at_100():
    r = score_resilience(
        EXPR,
        has_retry=True,
        has_healthcheck=True,
        has_timeout=True,
        has_lock=True,
        has_notify=True,
        is_high_frequency=False,
    )
    assert r.score <= 100


def test_factors_populated():
    r = score_resilience(EXPR, has_retry=True, has_lock=True)
    assert "retry configured" in r.factors
    assert "lock in place" in r.factors


def test_suggestions_populated_when_missing():
    r = score_resilience(EXPR)
    assert any("retry" in s.lower() for s in r.suggestions)
    assert any("healthcheck" in s.lower() for s in r.suggestions)


def test_str_output_contains_expression():
    r = score_resilience(EXPR)
    assert EXPR in str(r)


def test_str_output_contains_grade():
    r = score_resilience(EXPR)
    assert r.grade in str(r)


def test_grade_function():
    assert _grade(100) == "A"
    assert _grade(80) == "A"
    assert _grade(79) == "B"
    assert _grade(60) == "B"
    assert _grade(59) == "C"
    assert _grade(40) == "C"
    assert _grade(39) == "D"
    assert _grade(20) == "D"
    assert _grade(19) == "F"
    assert _grade(0) == "F"
