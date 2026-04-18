"""Tests for crontab_buddy.lint module."""

import pytest
from crontab_buddy.lint import lint, LintResult


def test_invalid_expression_returns_warning():
    result = lint("not a cron")
    assert not result.ok()
    assert any("Invalid" in w for w in result.warnings)


def test_every_minute_warns():
    result = lint("* * * * *")
    assert not result.ok()
    assert any("every minute" in w for w in result.warnings)


def test_specific_time_no_warnings():
    result = lint("30 9 * * 1")
    assert result.ok()
    assert result.warnings == []


def test_dom_and_dow_both_set_hint():
    result = lint("0 12 15 * 3")
    assert any("OR logic" in h for h in result.hints)


def test_redundant_step_warns():
    result = lint("*/1 * * * *")
    assert any("redundant" in w for w in result.warnings)


def test_midnight_hint():
    result = lint("0 0 * * *")
    assert any("midnight" in h or "@daily" in h for h in result.hints)


def test_large_minute_step_warns():
    result = lint("*/45 * * * *")
    assert any("once or twice" in w for w in result.warnings)


def test_large_hour_step_warns():
    result = lint("0 */13 * * *")
    assert any("once per day" in w for w in result.warnings)


def test_ok_returns_true_when_no_warnings():
    result = lint("15 10 * * *")
    assert result.ok() is True


def test_str_no_issues():
    result = lint("15 10 * * *")
    assert str(result) == "No issues found."


def test_str_contains_warn_label():
    result = lint("* * * * *")
    assert "[WARN]" in str(result)


def test_lint_result_defaults():
    r = LintResult()
    assert r.warnings == []
    assert r.hints == []
    assert r.ok() is True
