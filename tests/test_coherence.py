"""Tests for crontab_buddy.coherence."""

import pytest
from crontab_buddy.coherence import assess_coherence, CoherenceResult


def test_returns_coherence_result():
    result = assess_coherence("0 9 * * *")
    assert isinstance(result, CoherenceResult)


def test_clean_expression_scores_high():
    result = assess_coherence("0 9 * * *")
    assert result.score >= 0.9
    assert result.grade == "excellent"


def test_invalid_expression_is_incoherent():
    result = assess_coherence("not a cron")
    assert result.score == 0.0
    assert result.grade == "incoherent"
    assert any("parse error" in n for n in result.notes)


def test_dom_and_dow_both_set_penalised():
    result = assess_coherence("0 9 15 * 1")
    assert result.score < 1.0
    assert any("dom and dow" in n for n in result.notes)


def test_redundant_step_one_penalised():
    result = assess_coherence("*/1 * * * *")
    assert result.score < 1.0
    assert any("/1" in n or "redundant" in n for n in result.notes)


def test_inverted_range_penalised():
    result = assess_coherence("50-10 * * * *")
    assert result.score < 0.9
    assert any("inverted" in n for n in result.notes)


def test_duplicate_list_values_penalised():
    result = assess_coherence("5,5 * * * *")
    assert result.score < 1.0
    assert any("duplicate" in n or "single unique" in n for n in result.notes)


def test_no_notes_for_clean_expression():
    result = assess_coherence("30 6 * * 1-5")
    assert result.notes == []


def test_str_representation_contains_grade():
    result = assess_coherence("0 0 * * *")
    s = str(result)
    assert result.grade in s
    assert result.expression in s


def test_score_clamped_to_zero_on_many_issues():
    # step /1 on all five fields would deduct 0.5, plus inverted range
    result = assess_coherence("50-10 */1 */1 */1 */1")
    assert result.score >= 0.0


def test_grade_poor_for_low_score():
    result = assess_coherence("50-10 */1 15 * 1")
    assert result.grade in ("poor", "incoherent", "fair")


def test_multiple_deductions_accumulate():
    # dom+dow set AND redundant step
    result = assess_coherence("*/1 * 1 * 1")
    assert result.score <= 0.7
