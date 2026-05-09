"""Tests for crontab_buddy.resonance."""

import pytest
from crontab_buddy.resonance import assess_resonance, batch_resonance, ResonanceResult


def test_returns_resonance_result():
    r = assess_resonance("* * * * *", "* * * * *")
    assert isinstance(r, ResonanceResult)


def test_identical_expressions_are_harmonic():
    r = assess_resonance("* * * * *", "* * * * *")
    assert r.grade == "harmonic"
    assert r.score == pytest.approx(1.0)


def test_identical_expressions_shared_equals_total():
    r = assess_resonance("0 * * * *", "0 * * * *")
    assert r.shared_minutes == r.total_minutes
    assert r.score == pytest.approx(1.0)


def test_non_overlapping_expressions_are_silent():
    r = assess_resonance("0 0 * * *", "0 12 * * *")
    assert r.shared_minutes == 0
    assert r.grade == "silent"
    assert r.score == pytest.approx(0.0)


def test_partial_overlap():
    # every minute vs top of every hour — some overlap
    r = assess_resonance("* * * * *", "0 * * * *")
    assert 0.0 < r.score < 1.0


def test_invalid_expr_a_returns_error():
    r = assess_resonance("bad expr", "* * * * *")
    assert r.error is not None
    assert r.grade == "silent"
    assert r.score == 0.0


def test_invalid_expr_b_returns_error():
    r = assess_resonance("* * * * *", "not valid")
    assert r.error is not None


def test_score_between_zero_and_one():
    for expr_a, expr_b in [
        ("*/5 * * * *", "*/15 * * * *"),
        ("0 9 * * 1", "0 9 * * *"),
        ("30 6 * * *", "0 6 * * *"),
    ]:
        r = assess_resonance(expr_a, expr_b)
        assert 0.0 <= r.score <= 1.0


def test_step_expressions_share_correctly():
    # */15 fires at 0,15,30,45 — */30 fires at 0,30 — overlap is 0,30 each hour
    r = assess_resonance("*/15 * * * *", "*/30 * * * *")
    assert r.shared_minutes > 0
    assert r.score > 0.0


def test_batch_resonance_returns_list():
    results = batch_resonance("* * * * *", ["0 * * * *", "0 0 * * *"])
    assert len(results) == 2
    assert all(isinstance(r, ResonanceResult) for r in results)


def test_batch_resonance_base_preserved():
    results = batch_resonance("0 9 * * *", ["0 10 * * *", "0 9 * * *"])
    assert all(r.expression_a == "0 9 * * *" for r in results)


def test_str_no_error():
    r = assess_resonance("0 0 * * *", "0 0 * * *")
    s = str(r)
    assert "harmonic" in s
    assert "0 0 * * *" in s


def test_str_with_error():
    r = assess_resonance("bad", "* * * * *")
    s = str(r)
    assert "error" in s.lower()
