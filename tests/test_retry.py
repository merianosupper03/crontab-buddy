"""Tests for crontab_buddy.retry."""

import pytest

from crontab_buddy.retry import (
    set_retry,
    get_retry,
    delete_retry,
    list_retry_policies,
)


@pytest.fixture
def tmp_retry(tmp_path):
    return str(tmp_path / "retry.json")


def test_set_and_get_retry(tmp_retry):
    set_retry("0 * * * *", max_attempts=3, path=tmp_retry)
    result = get_retry("0 * * * *", path=tmp_retry)
    assert result is not None
    assert result["max_attempts"] == 3
    assert result["strategy"] == "fixed"
    assert result["delay_seconds"] == 60


def test_get_missing_returns_none(tmp_retry):
    assert get_retry("* * * * *", path=tmp_retry) is None


def test_overwrite_retry(tmp_retry):
    set_retry("0 * * * *", max_attempts=2, path=tmp_retry)
    set_retry("0 * * * *", max_attempts=5, strategy="exponential", path=tmp_retry)
    result = get_retry("0 * * * *", path=tmp_retry)
    assert result["max_attempts"] == 5
    assert result["strategy"] == "exponential"


def test_invalid_max_attempts_raises(tmp_retry):
    with pytest.raises(ValueError, match="max_attempts"):
        set_retry("0 * * * *", max_attempts=0, path=tmp_retry)


def test_invalid_strategy_raises(tmp_retry):
    with pytest.raises(ValueError, match="strategy"):
        set_retry("0 * * * *", max_attempts=3, strategy="random", path=tmp_retry)


def test_invalid_delay_raises(tmp_retry):
    with pytest.raises(ValueError, match="delay_seconds"):
        set_retry("0 * * * *", max_attempts=3, delay_seconds=-1, path=tmp_retry)


def test_delete_existing(tmp_retry):
    set_retry("0 * * * *", max_attempts=3, path=tmp_retry)
    assert delete_retry("0 * * * *", path=tmp_retry) is True
    assert get_retry("0 * * * *", path=tmp_retry) is None


def test_delete_missing_returns_false(tmp_retry):
    assert delete_retry("* * * * *", path=tmp_retry) is False


def test_list_retry_policies(tmp_retry):
    set_retry("0 * * * *", max_attempts=2, path=tmp_retry)
    set_retry("*/5 * * * *", max_attempts=4, strategy="linear", delay_seconds=30, path=tmp_retry)
    policies = list_retry_policies(path=tmp_retry)
    assert len(policies) == 2
    expressions = {p["expression"] for p in policies}
    assert "0 * * * *" in expressions
    assert "*/5 * * * *" in expressions


def test_list_empty_returns_empty_list(tmp_retry):
    assert list_retry_policies(path=tmp_retry) == []


def test_all_valid_strategies_accepted(tmp_retry):
    for i, strategy in enumerate(("fixed", "exponential", "linear")):
        expr = f"{i} * * * *"
        set_retry(expr, max_attempts=1, strategy=strategy, path=tmp_retry)
        result = get_retry(expr, path=tmp_retry)
        assert result["strategy"] == strategy
