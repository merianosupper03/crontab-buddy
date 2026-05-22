import pytest
from crontab_buddy.permeability import (
    assess_permeability,
    batch_permeability,
    PermeabilityResult,
    _field_permeability,
    _grade,
)


def test_returns_permeability_result():
    result = assess_permeability("* * * * *")
    assert isinstance(result, PermeabilityResult)


def test_invalid_expression_has_error():
    result = assess_permeability("bad expression")
    assert result.error is not None
    assert result.grade == "impermeable"
    assert result.score == 0.0


def test_all_wildcards_is_permeable():
    result = assess_permeability("* * * * *")
    assert result.grade == "permeable"
    assert result.score >= 0.85


def test_single_exact_time_is_impermeable_or_dense():
    result = assess_permeability("30 9 15 6 1")
    assert result.grade in ("impermeable", "dense", "restrictive")
    assert result.score < 0.5


def test_scores_dict_has_five_keys():
    result = assess_permeability("0 12 * * *")
    assert set(result.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_wildcard_field_scores_one():
    assert _field_permeability("*", 59) == 1.0


def test_exact_field_scores_zero():
    assert _field_permeability("5", 59) == 0.0


def test_step_field_scores_between_zero_and_one():
    score = _field_permeability("*/15", 59)
    assert 0.0 < score <= 1.0


def test_range_field_scores_between_zero_and_one():
    score = _field_permeability("9-17", 23)
    assert 0.0 < score <= 1.0


def test_list_field_scores_proportional():
    score = _field_permeability("1,2,3", 12)
    assert 0.0 < score <= 1.0


def test_grade_permeable():
    assert _grade(0.9) == "permeable"


def test_grade_semi_permeable():
    assert _grade(0.7) == "semi-permeable"


def test_grade_restrictive():
    assert _grade(0.5) == "restrictive"


def test_grade_dense():
    assert _grade(0.25) == "dense"


def test_grade_impermeable():
    assert _grade(0.1) == "impermeable"


def test_step_every_minute_high_permeability():
    result = assess_permeability("*/1 * * * *")
    assert result.score >= 0.7


def test_batch_returns_list():
    results = batch_permeability(["* * * * *", "0 0 * * *"])
    assert len(results) == 2
    assert all(isinstance(r, PermeabilityResult) for r in results)


def test_str_representation_no_error():
    result = assess_permeability("* * * * *")
    s = str(result)
    assert "permeable" in s
    assert "score=" in s


def test_str_representation_with_error():
    result = assess_permeability("not valid")
    s = str(result)
    assert "error=" in s
