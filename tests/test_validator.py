"""Tests for crontab_buddy.validator."""

import pytest
from crontab_buddy.validator import validate, ValidationResult


def test_valid_simple_expression():
    result = validate("0 9 * * 1")
    assert result.valid is True
    assert result.errors == []


def test_invalid_too_few_fields():
    result = validate("0 9 * *")
    assert result.valid is False
    assert len(result.errors) == 1


def test_invalid_out_of_range():
    result = validate("99 9 * * *")
    assert result.valid is False
    assert any("minute" in e.lower() or "99" in e for e in result.errors)


def test_bool_true_for_valid():
    result = validate("*/5 * * * *")
    assert bool(result) is True


def test_bool_false_for_invalid():
    result = validate("bad expression")
    assert bool(result) is False


def test_warning_every_minute():
    result = validate("* * * * *")
    assert result.valid is True
    assert any("every minute" in w for w in result.warnings)


def test_warning_dom_and_dow_both_set():
    result = validate("0 9 15 * 1")
    assert result.valid is True
    assert any("OR" in w for w in result.warnings)


def test_no_warning_when_only_dom_set():
    result = validate("0 9 15 * *")
    assert not any("OR" in w for w in result.warnings)


def test_no_warning_when_only_dow_set():
    result = validate("0 9 * * 1")
    assert not any("OR" in w for w in result.warnings)


def test_alias_expression_valid():
    result = validate("0 0 * * @weekly")
    # @weekly alias in dow position may or may not be supported;
    # just ensure it doesn't crash and returns a ValidationResult
    assert isinstance(result, ValidationResult)
