"""Tests for crontab_buddy.variable."""

from __future__ import annotations

import pytest
from pathlib import Path

from crontab_buddy.variable import (
    delete_variable,
    expand_variable,
    get_variable,
    list_variables,
    set_variable,
)


@pytest.fixture
def tmp_var(tmp_path):
    return tmp_path / "variables.json"


def test_set_and_get(tmp_var):
    set_variable("hourly", "0 * * * *", path=tmp_var)
    assert get_variable("hourly", path=tmp_var) == "0 * * * *"


def test_get_missing_returns_none(tmp_var):
    assert get_variable("missing", path=tmp_var) is None


def test_name_is_uppercased(tmp_var):
    set_variable("daily", "0 0 * * *", path=tmp_var)
    assert get_variable("DAILY", path=tmp_var) == "0 0 * * *"
    assert get_variable("daily", path=tmp_var) == "0 0 * * *"


def test_overwrite_variable(tmp_var):
    set_variable("x", "* * * * *", path=tmp_var)
    set_variable("x", "0 0 * * *", path=tmp_var)
    assert get_variable("x", path=tmp_var) == "0 0 * * *"


def test_delete_existing(tmp_var):
    set_variable("todelete", "* * * * *", path=tmp_var)
    result = delete_variable("todelete", path=tmp_var)
    assert result is True
    assert get_variable("todelete", path=tmp_var) is None


def test_delete_missing_returns_false(tmp_var):
    assert delete_variable("ghost", path=tmp_var) is False


def test_list_variables_empty(tmp_var):
    assert list_variables(path=tmp_var) == []


def test_list_variables_multiple(tmp_var):
    set_variable("b", "0 1 * * *", path=tmp_var)
    set_variable("a", "0 0 * * *", path=tmp_var)
    result = list_variables(path=tmp_var)
    names = [v["name"] for v in result]
    assert names == sorted(names)
    assert len(result) == 2


def test_expand_variable_returns_expression(tmp_var):
    set_variable("weekly", "0 0 * * 0", path=tmp_var)
    assert expand_variable("weekly", path=tmp_var) == "0 0 * * 0"


def test_expand_missing_returns_none(tmp_var):
    assert expand_variable("nope", path=tmp_var) is None
