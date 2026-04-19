"""Tests for crontab_buddy.copy module."""

import pytest
from crontab_buddy.copy import copy_expression, copy_with_dict, describe_diff
from crontab_buddy.parser import CronParseError


BASE = "30 6 * * 1"


def test_copy_no_overrides_returns_same_fields():
    result = copy_expression(BASE)
    assert str(result) == BASE


def test_copy_override_minute():
    result = copy_expression(BASE, minute="0")
    assert result.fields[0] == "0"
    assert result.fields[1] == "6"


def test_copy_override_multiple_fields():
    result = copy_expression(BASE, hour="12", dow="5")
    assert result.fields[1] == "12"
    assert result.fields[4] == "5"
    assert result.fields[0] == "30"  # unchanged


def test_copy_override_all_fields():
    result = copy_expression(BASE, minute="0", hour="0", dom="1", month="1", dow="*")
    assert str(result) == "0 0 1 1 *"


def test_copy_invalid_base_raises():
    with pytest.raises(CronParseError):
        copy_expression("bad expression here")


def test_copy_invalid_override_raises():
    with pytest.raises(CronParseError):
        copy_expression(BASE, minute="99")


def test_copy_with_dict_single_field():
    result = copy_with_dict(BASE, {"hour": "9"})
    assert result.fields[1] == "9"


def test_copy_with_dict_multiple_fields():
    result = copy_with_dict(BASE, {"minute": "15", "dow": "*"})
    assert result.fields[0] == "15"
    assert result.fields[4] == "*"


def test_copy_with_dict_unknown_field_raises():
    with pytest.raises(ValueError, match="Unknown field"):
        copy_with_dict(BASE, {"second": "0"})


def test_describe_diff_no_changes():
    diff = describe_diff(BASE, BASE)
    assert diff == {}


def test_describe_diff_single_change():
    modified = "0 6 * * 1"
    diff = describe_diff(BASE, modified)
    assert "minute" in diff
    assert diff["minute"]["before"] == "30"
    assert diff["minute"]["after"] == "0"


def test_describe_diff_multiple_changes():
    modified = "0 12 * * 5"
    diff = describe_diff(BASE, modified)
    assert set(diff.keys()) == {"minute", "hour", "dow"}
