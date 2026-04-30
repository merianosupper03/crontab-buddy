"""Tests for crontab_buddy.suppression."""

import pytest
from crontab_buddy.suppression import (
    suppress_expression,
    unsuppress_expression,
    is_suppressed,
    get_suppression,
    list_suppressions,
    clear_suppressions,
)


@pytest.fixture
def tmp_sup(tmp_path):
    return str(tmp_path / "suppressions.json")


EXPR = "0 9 * * 1"
EXPR2 = "*/5 * * * *"


def test_suppress_new_expression(tmp_sup):
    result = suppress_expression(EXPR, path=tmp_sup)
    assert result is True


def test_suppress_duplicate_returns_false(tmp_sup):
    suppress_expression(EXPR, path=tmp_sup)
    result = suppress_expression(EXPR, path=tmp_sup)
    assert result is False


def test_is_suppressed_true(tmp_sup):
    suppress_expression(EXPR, path=tmp_sup)
    assert is_suppressed(EXPR, path=tmp_sup) is True


def test_is_suppressed_false(tmp_sup):
    assert is_suppressed(EXPR, path=tmp_sup) is False


def test_unsuppress_existing(tmp_sup):
    suppress_expression(EXPR, path=tmp_sup)
    result = unsuppress_expression(EXPR, path=tmp_sup)
    assert result is True
    assert is_suppressed(EXPR, path=tmp_sup) is False


def test_unsuppress_missing_returns_false(tmp_sup):
    result = unsuppress_expression(EXPR, path=tmp_sup)
    assert result is False


def test_get_suppression_has_suppressed_at(tmp_sup):
    suppress_expression(EXPR, path=tmp_sup)
    info = get_suppression(EXPR, path=tmp_sup)
    assert info is not None
    assert "suppressed_at" in info


def test_get_suppression_stores_reason(tmp_sup):
    suppress_expression(EXPR, reason="maintenance", path=tmp_sup)
    info = get_suppression(EXPR, path=tmp_sup)
    assert info["reason"] == "maintenance"


def test_get_suppression_stores_until(tmp_sup):
    suppress_expression(EXPR, until="2099-01-01T00:00:00Z", path=tmp_sup)
    info = get_suppression(EXPR, path=tmp_sup)
    assert info["until"] == "2099-01-01T00:00:00Z"


def test_get_suppression_missing_returns_none(tmp_sup):
    assert get_suppression(EXPR, path=tmp_sup) is None


def test_list_suppressions_returns_all(tmp_sup):
    suppress_expression(EXPR, path=tmp_sup)
    suppress_expression(EXPR2, path=tmp_sup)
    result = list_suppressions(path=tmp_sup)
    assert EXPR in result
    assert EXPR2 in result


def test_clear_suppressions_returns_count(tmp_sup):
    suppress_expression(EXPR, path=tmp_sup)
    suppress_expression(EXPR2, path=tmp_sup)
    count = clear_suppressions(path=tmp_sup)
    assert count == 2


def test_clear_suppressions_empties_store(tmp_sup):
    suppress_expression(EXPR, path=tmp_sup)
    clear_suppressions(path=tmp_sup)
    assert list_suppressions(path=tmp_sup) == {}
