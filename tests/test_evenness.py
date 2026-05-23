"""Tests for crontab_buddy.evenness."""
import pytest
from crontab_buddy.evenness import assess_evenness, batch_evenness, EvennessResult


def test_returns_evenness_result():
    result = assess_evenness("*/5 * * * *")
    assert isinstance(result, EvennessResult)


def test_invalid_expression_has_error():
    result = assess_evenness("not valid")
    assert result.error is not None
    assert result.score == 0.0


def test_every_minute_is_perfectly_even():
    result = assess_evenness("* * * * *")
    assert result.score == pytest.approx(1.0, abs=0.01)
    assert result.grade == "perfectly even"


def test_every_five_minutes_is_perfectly_even():
    # */5 fires at 0,5,10,...,55 — perfectly uniform gaps
    result = assess_evenness("*/5 * * * *")
    assert result.score == pytest.approx(1.0, abs=0.01)


def test_every_fifteen_minutes_is_perfectly_even():
    result = assess_evenness("*/15 * * * *")
    assert result.score == pytest.approx(1.0, abs=0.01)


def test_single_firing_is_highly_uneven():
    result = assess_evenness("30 12 * * *")
    assert result.score == 0.0
    assert result.grade == "highly uneven"


def test_two_firings_equal_gap_is_perfectly_even():
    # 0 and 30 — gaps are 30 and 30, perfectly even
    result = assess_evenness("0,30 * * * *")
    assert result.score == pytest.approx(1.0, abs=0.01)


def test_uneven_list_has_lower_score():
    # 0,1,59 — very clustered
    result = assess_evenness("0,1,59 * * * *")
    assert result.score < 0.5


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 * * * *", "*/10 * * * *", "1,2,50 * * * *"]:
        r = assess_evenness(expr)
        assert 0.0 <= r.score <= 1.0


def test_grade_string_is_non_empty():
    result = assess_evenness("*/20 * * * *")
    assert isinstance(result.grade, str)
    assert len(result.grade) > 0


def test_str_representation_contains_expression():
    result = assess_evenness("*/5 * * * *")
    assert "*/5 * * * *" in str(result)


def test_str_representation_error_case():
    result = assess_evenness("bad expr")
    assert "error" in str(result).lower()


def test_batch_evenness_returns_list():
    results = batch_evenness(["* * * * *", "0 12 * * *"])
    assert isinstance(results, list)
    assert len(results) == 2


def test_batch_evenness_handles_invalid():
    results = batch_evenness(["* * * * *", "not valid"])
    assert results[0].error is None
    assert results[1].error is not None


def test_range_minute_evenness():
    # 0-4 fires at 0,1,2,3,4 — tightly clustered, low evenness
    result = assess_evenness("0-4 * * * *")
    assert result.score < 0.7
