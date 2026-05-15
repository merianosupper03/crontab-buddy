import pytest
from crontab_buddy.specificity import (
    assess_specificity,
    batch_specificity,
    SpecificityResult,
    _field_specificity,
    _grade,
)


def test_returns_specificity_result():
    result = assess_specificity("0 9 * * 1")
    assert isinstance(result, SpecificityResult)


def test_invalid_expression_has_error():
    result = assess_specificity("not valid")
    assert result.error is not None
    assert result.score == 0.0
    assert result.grade == "diffuse"


def test_all_wildcards_is_diffuse():
    result = assess_specificity("* * * * *")
    assert result.score == 0.0
    assert result.grade == "diffuse"


def test_all_exact_values_is_pinpoint():
    result = assess_specificity("30 9 15 6 2")
    assert result.score == 1.0
    assert result.grade == "pinpoint"


def test_scores_dict_has_five_keys():
    result = assess_specificity("0 12 * * *")
    assert set(result.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_exact_minute_scores_one():
    assert _field_specificity("30", 60) == 1.0


def test_wildcard_scores_zero():
    assert _field_specificity("*", 60) == 0.0


def test_step_expression_reduces_score():
    score = _field_specificity("*/15", 60)
    assert 0.0 < score < 1.0


def test_range_expression_reduces_score():
    score = _field_specificity("0-5", 60)
    assert 0.0 < score < 1.0


def test_list_expression_increases_with_count():
    score_two = _field_specificity("1,2", 60)
    score_four = _field_specificity("1,2,3,4", 60)
    assert score_four > score_two


def test_grade_pinpoint():
    assert _grade(0.9) == "pinpoint"


def test_grade_focused():
    assert _grade(0.7) == "focused"


def test_grade_moderate():
    assert _grade(0.5) == "moderate"


def test_grade_broad():
    assert _grade(0.3) == "broad"


def test_grade_diffuse():
    assert _grade(0.1) == "diffuse"


def test_partial_wildcards_intermediate_score():
    result = assess_specificity("0 9 * * *")
    assert 0.0 < result.score < 1.0


def test_batch_returns_list_of_results():
    results = batch_specificity(["* * * * *", "0 9 1 1 *"])
    assert len(results) == 2
    assert all(isinstance(r, SpecificityResult) for r in results)


def test_str_with_error():
    result = assess_specificity("bad")
    assert "error" in str(result)


def test_str_without_error():
    result = assess_specificity("0 9 * * *")
    s = str(result)
    assert "score" in s
    assert "grade" in s
