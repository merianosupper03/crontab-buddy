"""Tests for crontab_buddy.fidelity."""

import pytest
from crontab_buddy.fidelity import assess_fidelity, _field_score, _grade


# ---------------------------------------------------------------------------
# _field_score
# ---------------------------------------------------------------------------

def test_field_score_wildcard():
    assert _field_score("*") == 0.0


def test_field_score_plain_integer():
    assert _field_score("5") == 1.0


def test_field_score_step():
    assert _field_score("*/5") == pytest.approx(0.4)


def test_field_score_range():
    assert _field_score("1-5") == pytest.approx(0.6)


def test_field_score_list():
    assert _field_score("1,2,3") == pytest.approx(0.75)


# ---------------------------------------------------------------------------
# _grade
# ---------------------------------------------------------------------------

def test_grade_precise():
    assert _grade(0.9) == "precise"


def test_grade_moderate():
    assert _grade(0.7) == "moderate"


def test_grade_vague():
    assert _grade(0.5) == "vague"


def test_grade_unspecified():
    assert _grade(0.1) == "unspecified"


# ---------------------------------------------------------------------------
# assess_fidelity
# ---------------------------------------------------------------------------

def test_all_wildcards_is_unspecified():
    result = assess_fidelity("* * * * *")
    assert result.level == "unspecified"
    assert result.score == pytest.approx(0.0)


def test_fully_specified_is_precise():
    result = assess_fidelity("30 9 15 6 1")
    assert result.level == "precise"
    assert result.score == pytest.approx(1.0)


def test_invalid_expression_returns_unspecified():
    result = assess_fidelity("not a cron")
    assert result.level == "unspecified"
    assert result.score == 0.0
    assert any("parse error" in d for d in result.details)


def test_mixed_fields_moderate():
    # minute=30 (1.0), hour=* (0.0), dom=* (0.0), month=* (0.0), dow=* (0.0)
    result = assess_fidelity("30 * * * *")
    assert result.score == pytest.approx(0.2)
    assert result.level == "unspecified"


def test_step_fields_score_below_precise():
    result = assess_fidelity("*/5 */2 * * *")
    assert result.score < 0.5


def test_result_str_contains_expression():
    result = assess_fidelity("0 12 * * *")
    assert "0 12 * * *" in str(result)


def test_result_str_contains_level():
    result = assess_fidelity("0 12 * * *")
    assert result.level in str(result)


def test_details_lists_non_precise_fields():
    result = assess_fidelity("0 12 * * *")
    # dom, month, dow are wildcards — should appear in details
    assert len(result.details) > 0


def test_fully_specified_has_empty_details():
    result = assess_fidelity("30 9 15 6 1")
    assert result.details == []
