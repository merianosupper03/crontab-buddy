"""Tests for crontab_buddy.topology and topology_cli."""

import json
import pytest
from crontab_buddy.topology import assess_topology, TopologyResult, _field_constraint, _grade
from crontab_buddy.topology_cli import (
    cmd_topology_check,
    cmd_topology_score,
    cmd_topology_grade,
    cmd_topology_batch,
    cmd_topology_json,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


# --- unit tests for topology module ---

def test_returns_topology_result():
    result = assess_topology("* * * * *")
    assert isinstance(result, TopologyResult)


def test_all_wildcards_is_disconnected_or_flat():
    result = assess_topology("* * * * *")
    assert result.grade in ("disconnected", "sparse", "flat")
    assert result.score < 0.5


def test_invalid_expression_has_error():
    result = assess_topology("bad expr")
    assert result.error is not None
    assert result.grade == "disconnected"
    assert result.score == 0.0


def test_exact_expression_is_hierarchical_or_layered():
    result = assess_topology("30 6 * * 1")
    assert result.grade in ("hierarchical", "layered", "flat")
    assert result.score > 0.3


def test_field_scores_has_five_keys():
    result = assess_topology("0 12 * * *")
    assert set(result.field_scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_wildcard_field_score_is_zero():
    assert _field_constraint("*") == 0.0


def test_plain_integer_field_score_is_one():
    assert _field_constraint("5") == 1.0


def test_step_field_score_between_zero_and_one():
    score = _field_constraint("*/15")
    assert 0.0 < score <= 1.0


def test_range_field_score_between_zero_and_one():
    score = _field_constraint("1-5")
    assert 0.0 < score <= 1.0


def test_list_field_score_increases_with_items():
    score_two = _field_constraint("1,2")
    score_five = _field_constraint("1,2,3,4,5")
    assert score_five >= score_two


def test_grade_thresholds():
    assert _grade(0.9) == "hierarchical"
    assert _grade(0.7) == "layered"
    assert _grade(0.5) == "flat"
    assert _grade(0.1) == "sparse"
    assert _grade(0.0) == "disconnected"


# --- CLI tests ---

def captured(fn, *a, **kw):
    out = []
    fn(*a, print_fn=out.append, **kw)
    return out


def test_cmd_check_prints_expression():
    lines = captured(cmd_topology_check, Args(expression="0 9 * * 1"))
    assert any("0 9 * * 1" in l for l in lines)


def test_cmd_check_prints_grade():
    lines = captured(cmd_topology_check, Args(expression="0 9 * * 1"))
    assert any("Grade" in l for l in lines)


def test_cmd_check_invalid_expression_prints_error():
    lines = captured(cmd_topology_check, Args(expression="not valid"))
    assert any("Error" in l for l in lines)


def test_cmd_score_prints_float():
    lines = captured(cmd_topology_score, Args(expression="*/5 * * * *"))
    assert len(lines) == 1
    float(lines[0])  # should not raise


def test_cmd_grade_prints_label():
    lines = captured(cmd_topology_grade, Args(expression="0 0 * * *"))
    assert len(lines) == 1
    assert lines[0] in ("hierarchical", "layered", "flat", "sparse", "disconnected")


def test_cmd_batch_prints_one_line_per_expression():
    exprs = ["* * * * *", "0 12 * * *", "bad"]
    lines = captured(cmd_topology_batch, Args(expressions=exprs))
    assert len(lines) == 3


def test_cmd_json_outputs_valid_json():
    lines = captured(cmd_topology_json, Args(expression="30 6 * * 1"))
    data = json.loads("\n".join(lines))
    assert "score" in data
    assert "grade" in data
    assert "field_scores" in data
