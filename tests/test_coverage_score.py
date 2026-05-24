"""Tests for crontab_buddy.coverage_score."""

import pytest
from crontab_buddy.coverage_score import (
    compute_coverage_score,
    batch_coverage_score,
    _covered_hours,
    _grade,
)
from crontab_buddy.parser import CronExpression


# ---------------------------------------------------------------------------
# _grade helper
# ---------------------------------------------------------------------------

def test_grade_blanket():
    assert _grade(1.0) == "blanket"


def test_grade_broad():
    assert _grade(0.75) == "broad"


def test_grade_moderate():
    assert _grade(0.55) == "moderate"


def test_grade_sparse():
    assert _grade(0.35) == "sparse"


def test_grade_thin():
    assert _grade(0.15) == "thin"


def test_grade_bare():
    assert _grade(0.0) == "bare"


# ---------------------------------------------------------------------------
# _covered_hours helper
# ---------------------------------------------------------------------------

def test_covered_hours_wildcard():
    expr = CronExpression("* * * * *")
    assert _covered_hours(expr) == list(range(24))


def test_covered_hours_single():
    expr = CronExpression("0 9 * * *")
    assert _covered_hours(expr) == [9]


def test_covered_hours_range():
    expr = CronExpression("0 9-11 * * *")
    assert _covered_hours(expr) == [9, 10, 11]


def test_covered_hours_list():
    expr = CronExpression("0 6,12,18 * * *")
    assert _covered_hours(expr) == [6, 12, 18]


def test_covered_hours_step():
    expr = CronExpression("0 */6 * * *")
    assert _covered_hours(expr) == [0, 6, 12, 18]


# ---------------------------------------------------------------------------
# compute_coverage_score
# ---------------------------------------------------------------------------

def test_every_minute_is_blanket():
    r = compute_coverage_score("* * * * *")
    assert r.grade == "blanket"
    assert r.score == 1.0
    assert len(r.covered_hours) == 24


def test_single_hour_is_bare_or_thin():
    r = compute_coverage_score("0 3 * * *")
    assert r.score == pytest.approx(1 / 24, rel=1e-3)
    assert r.grade in ("bare", "thin")


def test_invalid_expression_has_error():
    r = compute_coverage_score("not a cron")
    assert r.error is not None
    assert r.score == 0.0
    assert r.grade == "bare"


def test_result_str_no_error():
    r = compute_coverage_score("0 */6 * * *")
    s = str(r)
    assert "score=" in s
    assert "grade=" in s


def test_result_str_with_error():
    r = compute_coverage_score("bad")
    assert "ERROR" in str(r)


# ---------------------------------------------------------------------------
# batch_coverage_score
# ---------------------------------------------------------------------------

def test_batch_returns_list():
    results = batch_coverage_score(["* * * * *", "0 9 * * *"])
    assert len(results) == 2


def test_batch_preserves_order():
    exprs = ["0 1 * * *", "0 2 * * *", "0 3 * * *"]
    results = batch_coverage_score(exprs)
    assert [r.expression for r in results] == exprs
