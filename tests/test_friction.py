import pytest
from crontab_buddy.friction import assess_friction, batch_friction, _field_friction, _grade


def test_returns_friction_result():
    r = assess_friction("0 9 * * 1")
    assert hasattr(r, "score")
    assert hasattr(r, "grade")
    assert hasattr(r, "scores")


def test_invalid_expression_has_error():
    r = assess_friction("bad expr")
    assert r.error is not None
    assert r.score == 0.0


def test_all_wildcards_is_frictionless():
    r = assess_friction("* * * * *")
    assert r.grade == "frictionless"
    assert r.score == 0.0


def test_all_exact_values_is_rigid_or_stiff():
    r = assess_friction("0 9 1 1 1")
    assert r.grade in ("rigid", "stiff", "moderate")
    assert r.score > 0.5


def test_scores_dict_has_five_keys():
    r = assess_friction("*/5 * * * *")
    assert set(r.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_wildcard_field_friction_is_zero():
    assert _field_friction("*", 60) == 0.0


def test_exact_field_friction_is_one():
    assert _field_friction("30", 60) == 1.0


def test_step_field_reduces_friction():
    score = _field_friction("*/2", 60)
    assert 0.0 < score < 1.0


def test_list_field_reduces_friction():
    score = _field_friction("1,2,3", 60)
    assert 0.0 < score < 1.0


def test_range_field_reduces_friction():
    score = _field_friction("0-29", 60)
    assert 0.0 < score < 1.0


def test_grade_rigid():
    assert _grade(0.90) == "rigid"


def test_grade_stiff():
    assert _grade(0.70) == "stiff"


def test_grade_moderate():
    assert _grade(0.50) == "moderate"


def test_grade_loose():
    assert _grade(0.30) == "loose"


def test_grade_frictionless():
    assert _grade(0.10) == "frictionless"


def test_batch_friction_returns_list():
    results = batch_friction(["* * * * *", "0 9 * * 1", "bad"])
    assert len(results) == 3


def test_batch_friction_invalid_has_error():
    results = batch_friction(["not valid"])
    assert results[0].error is not None


def test_score_between_zero_and_one():
    for expr in ["*/15 * * * *", "0 0 * * *", "0 12 1 * *", "30 6 * * 5"]:
        r = assess_friction(expr)
        assert 0.0 <= r.score <= 1.0


def test_str_representation_no_error():
    r = assess_friction("0 9 * * 1")
    assert "FrictionResult" in str(r)
    assert "score" in str(r)


def test_str_representation_with_error():
    r = assess_friction("oops")
    assert "error" in str(r)
