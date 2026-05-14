"""Tests for crontab_buddy.fuzziness."""

import pytest
from crontab_buddy.fuzziness import (
    assess_fuzziness,
    batch_fuzziness,
    _field_fuzziness,
    _grade,
    FuzzinessResult,
)


def test_returns_fuzziness_result():
    result = assess_fuzziness("* * * * *")
    assert isinstance(result, FuzzinessResult)


def test_all_wildcards_is_nebulous():
    result = assess_fuzziness("* * * * *")
    assert result.error is None
    assert result.overall == pytest.approx(1.0)
    assert result.grade == "nebulous"


def test_invalid_expression_has_error():
    result = assess_fuzziness("not a valid cron")
    assert result.error is not None
    assert result.overall == 0.0


def test_exact_single_time_is_crisp():
    result = assess_fuzziness("30 9 1 1 1")
    assert result.error is None
    assert result.overall == pytest.approx(0.0)
    assert result.grade == "crisp"


def test_scores_dict_has_five_keys():
    result = assess_fuzziness("*/5 * * * *")
    assert set(result.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_step_on_wildcard_raises_score():
    result = assess_fuzziness("*/5 * * * *")
    assert result.scores["minute"] > 0.0
    assert result.scores["hour"] == pytest.approx(1.0)


def test_list_fields_raise_score():
    result = assess_fuzziness("1,2,3 * * * *")
    assert result.scores["minute"] > 0.0


def test_range_field_moderate():
    result = assess_fuzziness("0 9-17 * * *")
    score = result.scores["hour"]
    assert 0.0 < score < 1.0


def test_batch_returns_list():
    results = batch_fuzziness(["* * * * *", "0 9 * * *"])
    assert len(results) == 2
    assert all(isinstance(r, FuzzinessResult) for r in results)


def test_batch_mixed_valid_invalid():
    results = batch_fuzziness(["* * * * *", "bad"])
    assert results[0].error is None
    assert results[1].error is not None


def test_field_fuzziness_wildcard():
    assert _field_fuzziness("*") == pytest.approx(1.0)


def test_field_fuzziness_exact():
    assert _field_fuzziness("5") == pytest.approx(0.0)


def test_field_fuzziness_step_star():
    score = _field_fuzziness("*/15")
    assert 0.0 < score < 1.0


def test_grade_crisp():
    assert _grade(0.1) == "crisp"


def test_grade_nebulous():
    assert _grade(0.9) == "nebulous"


def test_str_with_error():
    result = assess_fuzziness("bad")
    assert "error" in str(result).lower()


def test_str_without_error():
    result = assess_fuzziness("* * * * *")
    assert "nebulous" in str(result)
