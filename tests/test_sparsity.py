"""Tests for crontab_buddy.sparsity."""

import pytest

from crontab_buddy.sparsity import (
    SparsityResult,
    assess_sparsity,
    batch_sparsity,
    _grade,
)


# ---------------------------------------------------------------------------
# _grade helper
# ---------------------------------------------------------------------------

def test_grade_glacial():
    assert _grade(86400 * 31) == "glacial"


def test_grade_sparse():
    assert _grade(86400 * 8) == "sparse"


def test_grade_infrequent():
    assert _grade(86400) == "infrequent"


def test_grade_occasional():
    assert _grade(3600) == "occasional"


def test_grade_moderate():
    assert _grade(600) == "moderate"


def test_grade_dense():
    assert _grade(60) == "dense"


def test_grade_saturated():
    assert _grade(30) == "saturated"


# ---------------------------------------------------------------------------
# assess_sparsity
# ---------------------------------------------------------------------------

def test_returns_sparsity_result():
    r = assess_sparsity("0 9 * * 1")
    assert isinstance(r, SparsityResult)


def test_every_minute_is_dense_or_saturated():
    r = assess_sparsity("* * * * *")
    assert r.grade in ("dense", "saturated")


def test_every_minute_score_near_zero():
    r = assess_sparsity("* * * * *")
    assert r.score < 0.01


def test_weekly_is_sparse():
    r = assess_sparsity("0 9 * * 1")
    assert r.grade in ("sparse", "glacial", "infrequent")


def test_daily_midnight_is_infrequent_or_sparse():
    r = assess_sparsity("0 0 * * *")
    assert r.grade in ("infrequent", "sparse", "occasional")


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 * * * *", "0 0 * * *", "0 9 * * 1"]:
        r = assess_sparsity(expr)
        assert 0.0 <= r.score <= 1.0


def test_invalid_expression_has_error():
    r = assess_sparsity("invalid")
    assert r.error is not None
    assert r.grade == "unknown"


def test_invalid_expression_score_is_zero():
    r = assess_sparsity("99 99 99 99 99")
    assert r.score == 0.0


def test_interval_seconds_positive_for_valid():
    r = assess_sparsity("0 0 * * *")
    assert r.interval_seconds > 0


def test_str_contains_grade():
    r = assess_sparsity("0 0 * * *")
    assert r.grade in str(r)


def test_str_error_branch():
    r = assess_sparsity("bad expr")
    assert "error" in str(r).lower()


# ---------------------------------------------------------------------------
# batch_sparsity
# ---------------------------------------------------------------------------

def test_batch_returns_list():
    results = batch_sparsity(["* * * * *", "0 9 * * 1"])
    assert isinstance(results, list)
    assert len(results) == 2


def test_batch_preserves_order():
    exprs = ["* * * * *", "0 0 * * *", "0 9 * * 1"]
    results = batch_sparsity(exprs)
    for r, e in zip(results, exprs):
        assert r.expression == e
