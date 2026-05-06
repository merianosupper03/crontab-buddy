"""Tests for crontab_buddy.compliance."""

import pytest

from crontab_buddy.compliance import check_compliance, list_policies


def test_list_policies_returns_dict():
    policies = list_policies()
    assert isinstance(policies, dict)
    assert len(policies) > 0


def test_list_policies_contains_known_keys():
    policies = list_policies()
    assert "no_every_minute" in policies
    assert "weekdays_only" in policies


def test_invalid_expression_fails():
    result = check_compliance("not a cron")
    assert not result.passed
    assert any("Invalid" in v for v in result.violations)


def test_every_minute_violates_no_every_minute():
    result = check_compliance("* * * * *", policies=["no_every_minute"])
    assert not result.passed
    assert len(result.violations) == 1


def test_specific_time_passes_no_every_minute():
    result = check_compliance("30 9 * * *", policies=["no_every_minute"])
    assert result.passed
    assert result.violations == []


def test_wildcard_hour_violates_business_hours():
    result = check_compliance("0 * * * *", policies=["business_hours_only"])
    assert not result.passed
    assert any("business" in v.lower() for v in result.violations)


def test_business_hour_passes_business_hours():
    result = check_compliance("0 9 * * *", policies=["business_hours_only"])
    assert result.passed


def test_midnight_violates_business_hours():
    result = check_compliance("0 0 * * *", policies=["business_hours_only"])
    assert not result.passed


def test_wildcard_dow_violates_weekdays_only():
    result = check_compliance("0 9 * * *", policies=["weekdays_only"])
    assert not result.passed
    assert any("weekend" in v.lower() for v in result.violations)


def test_weekday_dow_passes_weekdays_only():
    result = check_compliance("0 9 * * 1", policies=["weekdays_only"])
    assert result.passed


def test_saturday_dow_violates_weekdays_only():
    result = check_compliance("0 9 * * 6", policies=["weekdays_only"])
    assert not result.passed


def test_multiple_violations_reported():
    result = check_compliance("* * * * *", policies=["no_every_minute", "weekdays_only"])
    assert not result.passed
    assert len(result.violations) >= 2


def test_bool_true_for_passing():
    result = check_compliance("30 9 * * 1", policies=["weekdays_only"])
    assert bool(result) is True


def test_bool_false_for_failing():
    result = check_compliance("* * * * *", policies=["no_every_minute"])
    assert bool(result) is False


def test_str_contains_pass():
    result = check_compliance("30 9 * * 1", policies=["weekdays_only"])
    assert "PASS" in str(result)


def test_str_contains_fail():
    result = check_compliance("* * * * *", policies=["no_every_minute"])
    assert "FAIL" in str(result)


def test_no_policies_uses_all_defaults():
    # wildcard expression should fail at least one default policy
    result = check_compliance("* * * * *")
    assert not result.passed
