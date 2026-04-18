import pytest
import json
import os
from crontab_buddy.aliases import set_alias, get_alias, delete_alias, list_aliases, resolve


@pytest.fixture
def tmp_aliases(tmp_path):
    return str(tmp_path / "aliases.json")


def test_set_and_get_alias(tmp_aliases):
    set_alias("midnight", "0 0 * * *", tmp_aliases)
    assert get_alias("midnight", tmp_aliases) == "0 0 * * *"


def test_get_missing_alias_returns_none(tmp_aliases):
    assert get_alias("nonexistent", tmp_aliases) is None


def test_alias_name_is_case_insensitive(tmp_aliases):
    set_alias("Daily", "0 9 * * *", tmp_aliases)
    assert get_alias("daily", tmp_aliases) == "0 9 * * *"
    assert get_alias("DAILY", tmp_aliases) == "0 9 * * *"


def test_overwrite_alias(tmp_aliases):
    set_alias("job", "0 0 * * *", tmp_aliases)
    set_alias("job", "5 4 * * *", tmp_aliases)
    assert get_alias("job", tmp_aliases) == "5 4 * * *"


def test_delete_existing_alias(tmp_aliases):
    set_alias("temp", "* * * * *", tmp_aliases)
    result = delete_alias("temp", tmp_aliases)
    assert result is True
    assert get_alias("temp", tmp_aliases) is None


def test_delete_missing_alias_returns_false(tmp_aliases):
    assert delete_alias("ghost", tmp_aliases) is False


def test_list_aliases_empty(tmp_aliases):
    assert list_aliases(tmp_aliases) == {}


def test_list_aliases_multiple(tmp_aliases):
    set_alias("a", "0 0 * * *", tmp_aliases)
    set_alias("b", "0 12 * * *", tmp_aliases)
    result = list_aliases(tmp_aliases)
    assert result["a"] == "0 0 * * *"
    assert result["b"] == "0 12 * * *"


def test_resolve_known_alias(tmp_aliases):
    set_alias("noon", "0 12 * * *", tmp_aliases)
    assert resolve("noon", tmp_aliases) == "0 12 * * *"


def test_resolve_unknown_returns_input(tmp_aliases):
    assert resolve("0 6 * * 1", tmp_aliases) == "0 6 * * 1"
