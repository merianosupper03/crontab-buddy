"""Tests for crontab_buddy.flow."""

import pytest
from crontab_buddy.flow import assess_flow, batch_flow, FlowResult


def test_returns_flow_result():
    result = assess_flow("* * * * *")
    assert isinstance(result, FlowResult)


def test_every_minute_has_no_error():
    result = assess_flow("* * * * *")
    assert result.error is None


def test_every_minute_is_fluid():
    result = assess_flow("* * * * *")
    assert result.grade == "fluid"


def test_every_minute_score_near_one():
    result = assess_flow("* * * * *")
    assert result.score >= 0.85


def test_every_minute_transitions_1440():
    result = assess_flow("* * * * *")
    assert result.transitions == 1440


def test_single_firing_is_erratic():
    result = assess_flow("30 9 * * 1")
    # Only fires once per week cycle in a single day view — very sparse
    assert result.grade in ("erratic", "choppy", "uneven", "smooth", "fluid")
    assert 0.0 <= result.score <= 1.0


def test_invalid_expression_has_error():
    result = assess_flow("99 99 99 99 99")
    assert result.error is not None
    assert result.score == 0.0
    assert result.grade == "erratic"


def test_hourly_is_fluid_or_smooth():
    result = assess_flow("0 * * * *")
    assert result.grade in ("fluid", "smooth")
    assert result.score >= 0.65


def test_step_every_15_minutes_is_fluid():
    result = assess_flow("*/15 * * * *")
    assert result.grade in ("fluid", "smooth")


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 * * * *", "0 9 * * *", "*/5 * * * *"]:
        r = assess_flow(expr)
        assert 0.0 <= r.score <= 1.0, f"Score out of range for {expr!r}: {r.score}"


def test_batch_flow_returns_list():
    results = batch_flow(["* * * * *", "0 * * * *", "invalid expr"])
    assert len(results) == 3


def test_batch_flow_invalid_entry_has_error():
    results = batch_flow(["bad expression"])
    assert results[0].error is not None


def test_transitions_equals_unique_firing_minutes():
    result = assess_flow("0 0,12 * * *")
    assert result.transitions == 2


def test_str_no_error():
    result = assess_flow("0 * * * *")
    s = str(result)
    assert "FlowResult" in s
    assert "fluid" in s or "smooth" in s or "uneven" in s or "choppy" in s or "erratic" in s


def test_str_with_error():
    result = assess_flow("bad")
    s = str(result)
    assert "error" in s
