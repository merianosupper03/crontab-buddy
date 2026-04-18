"""Tests for crontab_buddy.diff."""

import pytest
from crontab_buddy.diff import diff_expressions, expressions_equal
from crontab_buddy.parser import CronParseError


def test_identical_expressions_no_diff():
    assert diff_expressions("0 * * * *", "0 * * * *") == []


def test_single_field_change():
    changes = diff_expressions("0 * * * *", "5 * * * *")
    assert len(changes) == 1
    assert "minute" in changes[0]
    assert "'0'" in changes[0]
    assert "'5'" in changes[0]


def test_multiple_field_changes():
    changes = diff_expressions("0 0 * * *", "*/5 12 1 * *")
    assert len(changes) == 3
    fields_mentioned = [c.split(":")[0] for c in changes]
    assert "minute" in fields_mentioned
    assert "hour" in fields_mentioned
    assert "day-of-month" in fields_mentioned


def test_all_fields_changed():
    changes = diff_expressions("0 0 1 1 0", "59 23 31 12 6")
    assert len(changes) == 5


def test_expressions_equal_true():
    assert expressions_equal("*/15 * * * *", "*/15 * * * *") is True


def test_expressions_equal_false():
    assert expressions_equal("0 * * * *", "0 12 * * *") is False


def test_invalid_expression_raises():
    with pytest.raises(CronParseError):
        diff_expressions("bad expr", "0 * * * *")
