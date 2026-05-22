"""Tests for crontab_buddy.elasticity."""

import pytest
from crontab_buddy.elasticity import assess_elasticity, batch_elasticity, _field_elasticity, _grade


def test_returns_elasticity_result():
    r = assess_elasticity("* * * * *")
    assert r.expression == "* * * * *"
    assert r.score is not None
    assert r.grade is not None
    assert isinstance(r.scores, dict)


def test_invalid_expression_has_error():
    r = assess_elasticity("not valid")
    assert r.error is not None
    assert r.score == 0.0
    assert r.grade == "rigid"


def test_all_wildcards_is_supple():
    r = assess_elasticity("* * * * *")
    assert r.score == 1.0
    assert r.grade == "supple"


def test_single_exact_time_is_rigid_or_stiff():
    r = assess_elasticity("30 9 15 6 1")
    assert r.grade in ("rigid", "stiff")
    assert r.score < 0.3


def test_scores_dict_has_five_keys():
    r = assess_elasticity("*/5 * * * *")
    assert set(r.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_step_minute_raises_score():
    r_exact = assess_elasticity("30 * * * *")
    r_step = assess_elasticity("*/5 * * * *")
    assert r_step.score > r_exact.score


def test_list_field_raises_score():
    r_single = assess_elasticity("0 9 * * *")
    r_list = assess_elasticity("0 9,12,15,18 * * *")
    assert r_list.score > r_single.score


def test_range_field_raises_score():
    r_exact = assess_elasticity("0 9 * * *")
    r_range = assess_elasticity("0 8-17 * * *")
    assert r_range.score > r_exact.score


def test_field_elasticity_wildcard_is_one():
    assert _field_elasticity("*", 59) == 1.0


def test_field_elasticity_exact_is_low():
    assert _field_elasticity("30", 59) == pytest.approx(0.05)


def test_field_elasticity_step_scales():
    val = _field_elasticity("*/2", 60)
    assert 0.0 < val <= 1.0


def test_grade_supple():
    assert _grade(0.9) == "supple"


def test_grade_rigid():
    assert _grade(0.1) == "rigid"


def test_batch_elasticity_returns_list():
    results = batch_elasticity(["* * * * *", "0 9 * * *", "bad expr"])
    assert len(results) == 3


def test_batch_elasticity_errors_marked():
    results = batch_elasticity(["bad"])
    assert results[0].error is not None


def test_str_with_error():
    r = assess_elasticity("bad")
    assert "error" in str(r).lower()


def test_str_without_error():
    r = assess_elasticity("* * * * *")
    s = str(r)
    assert "supple" in s
    assert "1.000" in s
