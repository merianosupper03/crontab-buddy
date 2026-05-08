"""Tests for crontab_buddy.fluency."""
import pytest
from crontab_buddy.fluency import (
    assess_fluency,
    batch_fluency,
    FluencyResult,
    _field_fluency,
    _grade,
)


def test_returns_fluency_result():
    r = assess_fluency("0 9 * * 1")
    assert isinstance(r, FluencyResult)


def test_all_wildcards_is_eloquent():
    r = assess_fluency("* * * * *")
    assert r.grade == "eloquent"
    assert r.score >= 0.85


def test_invalid_expression_has_error():
    r = assess_fluency("not a cron")
    assert r.error != ""
    assert r.score == 0.0
    assert r.grade == "opaque"


def test_plain_integers_score_high():
    r = assess_fluency("30 8 1 1 1")
    assert r.score >= 0.70


def test_step_expression_is_readable():
    r = assess_fluency("*/15 * * * *")
    assert r.score >= 0.55


def test_dom_and_dow_both_set_penalised():
    r_both = assess_fluency("0 12 15 * 3")
    r_only_dom = assess_fluency("0 12 15 * *")
    assert r_both.score <= r_only_dom.score
    assert any("DOM" in n or "DOW" in n for n in r_both.notes)


def test_long_list_penalised():
    r = assess_fluency("1,2,3,4,5,6,7 * * * *")
    r_simple = assess_fluency("0 * * * *")
    assert r.score < r_simple.score


def test_field_fluency_wildcard():
    assert _field_fluency("*") == 1.0


def test_field_fluency_plain_integer():
    assert _field_fluency("5") == 0.95


def test_field_fluency_step():
    score = _field_fluency("*/5")
    assert 0.5 < score < 1.0


def test_field_fluency_range():
    score = _field_fluency("1-5")
    assert 0.4 < score < 0.9


def test_field_fluency_list_digits():
    score = _field_fluency("1,2,3")
    assert 0.2 < score < 0.9


def test_grade_boundaries():
    assert _grade(1.0) == "eloquent"
    assert _grade(0.85) == "eloquent"
    assert _grade(0.65) == "clear"
    assert _grade(0.45) == "readable"
    assert _grade(0.25) == "cryptic"
    assert _grade(0.0) == "opaque"


def test_batch_fluency_returns_list():
    results = batch_fluency(["* * * * *", "0 9 * * 1", "bad expr"])
    assert len(results) == 3
    assert all(isinstance(r, FluencyResult) for r in results)


def test_batch_fluency_mixed_valid_invalid():
    results = batch_fluency(["* * * * *", "not valid"])
    assert results[0].error == ""
    assert results[1].error != ""


def test_str_with_error():
    r = assess_fluency("bad")
    assert "error=" in str(r)


def test_str_without_error():
    r = assess_fluency("* * * * *")
    assert "grade=" in str(r)
    assert "score=" in str(r)
