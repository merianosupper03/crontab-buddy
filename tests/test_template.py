import pytest
from crontab_buddy.template import (
    list_templates,
    get_template,
    search_templates,
    template_to_expression,
)
from crontab_buddy.parser import CronExpression


def test_list_templates_returns_all():
    templates = list_templates()
    assert len(templates) == 10
    assert all("name" in t and "expression" in t for t in templates)


def test_list_templates_have_descriptions():
    for t in list_templates():
        assert "description" in t
        assert len(t["description"]) > 0


def test_get_template_known():
    t = get_template("daily-midnight")
    assert t is not None
    assert t["expression"] == "0 0 * * *"
    assert t["name"] == "daily-midnight"


def test_get_template_unknown_returns_none():
    assert get_template("nonexistent") is None


def test_get_template_case_insensitive():
    t = get_template("DAILY-MIDNIGHT")
    assert t is not None
    assert t["expression"] == "0 0 * * *"


def test_search_templates_by_name():
    results = search_templates("daily")
    names = [r["name"] for r in results]
    assert "daily-midnight" in names
    assert "daily-noon" in names


def test_search_templates_by_tag():
    results = search_templates("business")
    assert len(results) == 1
    assert results[0]["name"] == "weekdays-9am"


def test_search_templates_by_description():
    results = search_templates("noon")
    names = [r["name"] for r in results]
    assert "daily-noon" in names


def test_search_templates_no_match():
    results = search_templates("zzznomatch")
    assert results == []


def test_template_to_expression_valid():
    expr = template_to_expression("every-hour")
    assert isinstance(expr, CronExpression)
    assert expr.hour == "*"
    assert expr.minute == "0"


def test_template_to_expression_unknown_returns_none():
    assert template_to_expression("ghost-template") is None


def test_all_templates_parse_successfully():
    for t in list_templates():
        expr = template_to_expression(t["name"])
        assert expr is not None, f"Template '{t['name']}' failed to parse"
