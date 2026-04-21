"""Tests for crontab_buddy.condition module."""

import json
import pytest
from pathlib import Path

from crontab_buddy.condition import (
    VALID_OPERATORS,
    add_condition,
    clear_conditions,
    get_conditions,
    list_all_conditions,
    remove_condition,
)


@pytest.fixture()
def tmp_cond(tmp_path):
    return tmp_path / "conditions.json"


def test_add_and_get(tmp_cond):
    add_condition("0 * * * *", "ENV", "==", "prod", data_file=tmp_cond)
    rules = get_conditions("0 * * * *", data_file=tmp_cond)
    assert len(rules) == 1
    assert rules[0] == {"variable": "ENV", "operator": "==", "value": "prod"}


def test_add_duplicate_returns_false(tmp_cond):
    add_condition("0 * * * *", "ENV", "==", "prod", data_file=tmp_cond)
    result = add_condition("0 * * * *", "ENV", "==", "prod", data_file=tmp_cond)
    assert result is False
    assert len(get_conditions("0 * * * *", data_file=tmp_cond)) == 1


def test_add_multiple_conditions(tmp_cond):
    add_condition("0 * * * *", "ENV", "==", "prod", data_file=tmp_cond)
    add_condition("0 * * * *", "LOAD", "<", "0.8", data_file=tmp_cond)
    rules = get_conditions("0 * * * *", data_file=tmp_cond)
    assert len(rules) == 2


def test_get_missing_returns_empty(tmp_cond):
    result = get_conditions("0 0 * * *", data_file=tmp_cond)
    assert result == []


def test_remove_existing(tmp_cond):
    add_condition("0 * * * *", "ENV", "==", "prod", data_file=tmp_cond)
    removed = remove_condition("0 * * * *", "ENV", "==", "prod", data_file=tmp_cond)
    assert removed is True
    assert get_conditions("0 * * * *", data_file=tmp_cond) == []


def test_remove_missing_returns_false(tmp_cond):
    result = remove_condition("0 * * * *", "ENV", "==", "prod", data_file=tmp_cond)
    assert result is False


def test_remove_cleans_up_empty_key(tmp_cond):
    add_condition("0 * * * *", "ENV", "==", "prod", data_file=tmp_cond)
    remove_condition("0 * * * *", "ENV", "==", "prod", data_file=tmp_cond)
    data = json.loads(tmp_cond.read_text())
    assert "0 * * * *" not in data


def test_clear_conditions(tmp_cond):
    add_condition("0 * * * *", "A", "==", "1", data_file=tmp_cond)
    add_condition("0 * * * *", "B", "!=", "2", data_file=tmp_cond)
    count = clear_conditions("0 * * * *", data_file=tmp_cond)
    assert count == 2
    assert get_conditions("0 * * * *", data_file=tmp_cond) == []


def test_clear_missing_returns_zero(tmp_cond):
    count = clear_conditions("0 0 * * *", data_file=tmp_cond)
    assert count == 0


def test_invalid_operator_raises(tmp_cond):
    with pytest.raises(ValueError, match="Invalid operator"):
        add_condition("0 * * * *", "ENV", "~~", "prod", data_file=tmp_cond)


def test_list_all_conditions(tmp_cond):
    add_condition("0 * * * *", "ENV", "==", "prod", data_file=tmp_cond)
    add_condition("0 0 * * *", "LOAD", "<", "0.5", data_file=tmp_cond)
    all_cond = list_all_conditions(data_file=tmp_cond)
    assert "0 * * * *" in all_cond
    assert "0 0 * * *" in all_cond


def test_all_valid_operators_accepted(tmp_cond):
    for i, op in enumerate(VALID_OPERATORS):
        result = add_condition(f"0 {i} * * *", "X", op, "val", data_file=tmp_cond)
        assert result is True
