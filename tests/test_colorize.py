"""Tests for crontab_buddy.colorize."""

import pytest
import crontab_buddy.colorize as colorize_mod
from crontab_buddy.colorize import colorize_expression, colorize_description, field_legend


@pytest.fixture(autouse=True)
def disable_colors(monkeypatch):
    """Force colors off so output is predictable in tests."""
    monkeypatch.setattr(colorize_mod, "TRY_COLORS", False)


def test_colorize_expression_five_fields():
    result = colorize_expression("* * * * *")
    assert "*" in result
    assert result.count("*") == 5


def test_colorize_expression_wrong_field_count():
    bad = "* * *"
    assert colorize_expression(bad) == bad


def test_colorize_expression_preserves_fields():
    expr = "0 9 * * 1"
    result = colorize_expression(expr)
    for field in ["0", "9", "*", "1"]:
        assert field in result


def test_colorize_expression_separates_fields():
    result = colorize_expression("0 9 * * 1")
    # With colors off, fields are joined by double space
    assert "  " in result


def test_colorize_description_returns_string():
    desc = "every day at 9am"
    result = colorize_description(desc)
    assert isinstance(result, str)
    assert desc in result


def test_colorize_description_no_color_passthrough():
    desc = "At midnight on Sundays"
    assert colorize_description(desc) == desc


def test_field_legend_contains_all_names():
    legend = field_legend()
    for name in ["minute", "hour", "day-of-month", "month", "day-of-week"]:
        assert name in legend


def test_field_legend_is_string():
    assert isinstance(field_legend(), str)
