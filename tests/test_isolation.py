"""Tests for crontab_buddy.isolation."""
import pytest
from crontab_buddy.isolation import assess_isolation, IsolationResult, _grade


def test_returns_isolation_result():
    r = assess_isolation("0 * * * *")
    assert isinstance(r, IsolationResult)


def test_invalid_expression_has_error():
    r = assess_isolation("not a cron")
    assert r.error is not None
    assert r.score == 0.0
    assert r.grade == "crowded"


def test_no_peers_gives_full_isolation():
    r = assess_isolation("0 9 * * *", peers=[])
    assert r.error is None
    assert r.score == 1.0
    assert r.grade == "isolated"
    assert r.neighbours == 0


def test_identical_peer_reduces_isolation():
    r = assess_isolation("0 9 * * *", peers=["0 9 * * *"])
    assert r.error is None
    assert r.score < 1.0
    assert r.neighbours > 0


def test_non_overlapping_peer_keeps_full_isolation():
    # fires at minute 0 of hour 9; peer fires at minute 0 of hour 22 — no overlap
    r = assess_isolation("0 9 * * *", peers=["0 22 * * *"])
    assert r.error is None
    assert r.score == 1.0


def test_every_minute_with_peer_has_many_neighbours():
    r = assess_isolation("* * * * *", peers=["* * * * *"])
    assert r.error is None
    assert r.neighbours > 0
    assert r.score < 1.0


def test_grade_isolated():
    assert _grade(0.9) == "isolated"


def test_grade_sparse():
    assert _grade(0.7) == "sparse"


def test_grade_moderate():
    assert _grade(0.5) == "moderate"


def test_grade_crowded():
    assert _grade(0.1) == "crowded"


def test_score_is_between_zero_and_one():
    r = assess_isolation("*/15 * * * *", peers=["*/5 * * * *"])
    assert 0.0 <= r.score <= 1.0


def test_invalid_peer_is_skipped():
    r = assess_isolation("0 9 * * *", peers=["not valid"])
    assert r.error is None
    assert r.score == 1.0


def test_str_no_error():
    r = assess_isolation("0 9 * * *")
    s = str(r)
    assert "score=" in s
    assert "grade=" in s


def test_str_with_error():
    r = assess_isolation("bad")
    s = str(r)
    assert "error=" in s
