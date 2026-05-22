"""Tests for crontab_buddy.porosity."""
import pytest
from crontab_buddy.porosity import assess_porosity, batch_porosity, _field_porosity, _grade


def test_returns_porosity_result():
    result = assess_porosity("* * * * *")
    assert result.expression == "* * * * *"
    assert result.score is not None
    assert result.grade is not None


def test_invalid_expression_has_error():
    result = assess_porosity("not valid")
    assert result.error is not None
    assert result.score == 0.0
    assert result.grade == "sealed"


def test_all_wildcards_is_porous():
    result = assess_porosity("* * * * *")
    assert result.score == 1.0
    assert result.grade == "porous"


def test_single_exact_time_is_dense_or_sealed():
    result = assess_porosity("30 9 * * *")
    # minute=30 (0.0), hour=9 (0.0), dom=* (1.0), month=* (1.0), dow=* (1.0)
    assert result.score == pytest.approx(0.6, abs=0.05)
    assert result.grade in ("semi-open", "open")


def test_scores_dict_has_five_keys():
    result = assess_porosity("* * * * *")
    assert set(result.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_field_porosity_wildcard():
    assert _field_porosity("*", 60) == 1.0


def test_field_porosity_exact_value():
    assert _field_porosity("5", 60) == 0.0


def test_field_porosity_list_reduces_score():
    score = _field_porosity("1,2,3,4,5,6", 60)
    assert 0.0 < score < 1.0


def test_field_porosity_range():
    score = _field_porosity("0-29", 60)
    assert score == pytest.approx(0.5, abs=0.02)


def test_field_porosity_step_star():
    score = _field_porosity("*/2", 60)
    assert 0.0 < score < 1.0


def test_grade_porous():
    assert _grade(0.95) == "porous"


def test_grade_open():
    assert _grade(0.75) == "open"


def test_grade_semi_open():
    assert _grade(0.50) == "semi-open"


def test_grade_dense():
    assert _grade(0.30) == "dense"


def test_grade_sealed():
    assert _grade(0.10) == "sealed"


def test_batch_porosity_returns_list():
    results = batch_porosity(["* * * * *", "0 9 * * 1", "bad expr"])
    assert len(results) == 3


def test_batch_porosity_invalid_has_error():
    results = batch_porosity(["bad"])
    assert results[0].error is not None


def test_str_no_error():
    result = assess_porosity("* * * * *")
    s = str(result)
    assert "porous" in s


def test_str_with_error():
    result = assess_porosity("bad")
    s = str(result)
    assert "error" in s
