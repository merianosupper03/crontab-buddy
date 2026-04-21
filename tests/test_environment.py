"""Tests for crontab_buddy.environment module."""

from __future__ import annotations

import pytest
from pathlib import Path

from crontab_buddy.environment import (
    set_env_var,
    get_env_var,
    get_all_env_vars,
    delete_env_var,
    clear_env_vars,
    list_all_env_vars,
)


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path / "environments.json"


def test_set_and_get(tmp_env):
    set_env_var("* * * * *", "PATH", "/usr/bin", tmp_env)
    assert get_env_var("* * * * *", "PATH", tmp_env) == "/usr/bin"


def test_get_missing_returns_none(tmp_env):
    assert get_env_var("* * * * *", "MISSING", tmp_env) is None


def test_key_is_uppercased(tmp_env):
    set_env_var("0 * * * *", "home", "/root", tmp_env)
    assert get_env_var("0 * * * *", "HOME", tmp_env) == "/root"
    assert get_env_var("0 * * * *", "home", tmp_env) == "/root"


def test_overwrite_env_var(tmp_env):
    set_env_var("0 0 * * *", "FOO", "bar", tmp_env)
    set_env_var("0 0 * * *", "FOO", "baz", tmp_env)
    assert get_env_var("0 0 * * *", "FOO", tmp_env) == "baz"


def test_get_all_env_vars(tmp_env):
    set_env_var("5 4 * * *", "A", "1", tmp_env)
    set_env_var("5 4 * * *", "B", "2", tmp_env)
    env = get_all_env_vars("5 4 * * *", tmp_env)
    assert env == {"A": "1", "B": "2"}


def test_get_all_env_vars_empty(tmp_env):
    assert get_all_env_vars("1 2 3 4 5", tmp_env) == {}


def test_delete_env_var(tmp_env):
    set_env_var("* * * * 1", "KEY", "val", tmp_env)
    result = delete_env_var("* * * * 1", "KEY", tmp_env)
    assert result is True
    assert get_env_var("* * * * 1", "KEY", tmp_env) is None


def test_delete_missing_returns_false(tmp_env):
    assert delete_env_var("* * * * *", "NOPE", tmp_env) is False


def test_clear_env_vars(tmp_env):
    set_env_var("0 12 * * *", "X", "1", tmp_env)
    set_env_var("0 12 * * *", "Y", "2", tmp_env)
    clear_env_vars("0 12 * * *", tmp_env)
    assert get_all_env_vars("0 12 * * *", tmp_env) == {}


def test_list_all_env_vars(tmp_env):
    set_env_var("* * * * *", "A", "1", tmp_env)
    set_env_var("0 0 * * *", "B", "2", tmp_env)
    all_envs = list_all_env_vars(tmp_env)
    assert "* * * * *" in all_envs
    assert "0 0 * * *" in all_envs


def test_multiple_expressions_isolated(tmp_env):
    set_env_var("expr1", "FOO", "one", tmp_env)
    set_env_var("expr2", "FOO", "two", tmp_env)
    assert get_env_var("expr1", "FOO", tmp_env) == "one"
    assert get_env_var("expr2", "FOO", tmp_env) == "two"
