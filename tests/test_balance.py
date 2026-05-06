"""Tests for crontab_buddy.balance"""

import pytest
from crontab_buddy.balance import assess_balance, BalanceResult


def test_all_wildcards_returns_excellent():
    result = assess_balance("* * * * *")
    assert result.grade == "excellent"
    assert result.score >= 0.85


def test_invalid_expression_returns_poor():
    result = assess_balance("not a cron")
    assert result.grade == "poor"
    assert result.score == 0.0
    assert any("Invalid" in n for n in result.notes)


def test_exact_single_time_is_concentrated():
    # runs once a day at a fixed minute/hour — low spread on minute+hour
    result = assess_balance("30 2 * * *")
    assert result.score < 0.85


def test_step_minute_improves_score():
    every5  = assess_balance("*/5 * * * *")
    exact   = assess_balance("0 * * * *")
    # distributing across minutes should score >= exact single minute
    assert every5.score >= exact.score


def test_list_fields_increase_spread():
    single = assess_balance("0 2 * * *")
    multi  = assess_balance("0 2,8,14,20 * * *")
    assert multi.score > single.score


def test_range_field_increases_spread():
    single = assess_balance("0 2 * * *")
    ranged = assess_balance("0 2-22 * * *")
    assert ranged.score > single.score


def test_result_is_balance_result_instance():
    result = assess_balance("*/15 * * * *")
    assert isinstance(result, BalanceResult)


def test_notes_not_empty():
    result = assess_balance("0 0 1 1 0")
    assert len(result.notes) > 0


def test_str_contains_expression():
    result = assess_balance("0 12 * * 1")
    text = str(result)
    assert "0 12 * * 1" in text


def test_str_contains_grade():
    result = assess_balance("* * * * *")
    assert result.grade in str(result)


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 0 1 1 0", "*/10 */6 * * *", "30 14 * * 5"]:
        r = assess_balance(expr)
        assert 0.0 <= r.score <= 1.0, f"score out of range for {expr}: {r.score}"


def test_fully_specific_expression_is_poor_or_fair():
    # every field pinned to a single value
    result = assess_balance("30 14 15 6 3")
    assert result.grade in ("poor", "fair")
