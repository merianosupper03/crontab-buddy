"""Tests for crontab_buddy.clutter."""

import pytest
from crontab_buddy.clutter import assess_clutter, batch_clutter, _field_clutter, _grade


def test_returns_clutter_result():
    result = assess_clutter("0 12 * * *")
    assert result.expression == "0 12 * * *"
    assert result.grade
    assert isinstance(result.score, float)


def test_invalid_expression_has_error():
    result = assess_clutter("not valid")
    assert result.error is not None
    assert result.score == 1.0
    assert result.grade == "chaotic"


def test_all_wildcards_is_minimal():
    result = assess_clutter("* * * * *")
    assert result.grade == "minimal"
    assert result.score == 0.0


def test_single_exact_time_is_tidy_or_minimal():
    result = assess_clutter("30 6 * * *")
    assert result.grade in ("minimal", "tidy")
    assert result.score < 0.45


def test_list_fields_raise_score():
    result = assess_clutter("0,15,30,45 * * * *")
    assert result.score > 0.2


def test_complex_expression_is_cluttered_or_chaotic():
    result = assess_clutter("0,15,30 8-18/2 1-15,20 1,6 1-5")
    assert result.grade in ("cluttered", "chaotic", "moderate")


def test_scores_dict_has_five_keys():
    result = assess_clutter("* * * * *")
    assert set(result.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_step_on_wildcard_is_low_clutter():
    result = assess_clutter("*/15 * * * *")
    assert result.scores["minute"] == pytest.approx(0.2)


def test_range_field_moderate_clutter():
    score = _field_clutter("8-18")
    assert 0.3 < score < 0.7


def test_range_with_step_is_higher():
    score = _field_clutter("8-18/2")
    assert score > _field_clutter("8-18")


def test_grade_thresholds():
    assert _grade(0.0) == "minimal"
    assert _grade(0.25) == "tidy"
    assert _grade(0.45) == "moderate"
    assert _grade(0.65) == "cluttered"
    assert _grade(0.85) == "chaotic"


def test_batch_clutter_returns_list():
    results = batch_clutter(["* * * * *", "0 12 * * *", "bad"])
    assert len(results) == 3


def test_batch_clutter_handles_invalid():
    results = batch_clutter(["bad expression"])
    assert results[0].error is not None


def test_str_with_error():
    result = assess_clutter("nope")
    s = str(result)
    assert "error" in s.lower()


def test_str_without_error():
    result = assess_clutter("0 0 * * *")
    s = str(result)
    assert "grade" in s.lower()
