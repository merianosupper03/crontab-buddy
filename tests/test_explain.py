import pytest
from crontab_buddy.explain import explain, _explain_field


def test_explain_returns_five_fields():
    result = explain("0 9 * * 1")
    assert len(result) == 5


def test_explain_field_names():
    result = explain("0 9 * * 1")
    names = [r["field"] for r in result]
    assert names == ["minute", "hour", "day-of-month", "month", "day-of-week"]


def test_explain_wildcard():
    result = explain("* * * * *")
    assert "every" in result[0]["description"]
    assert "every" in result[2]["description"]


def test_explain_exact_minute():
    result = explain("30 * * * *")
    assert "exactly 30" in result[0]["description"]


def test_explain_step():
    result = explain("*/15 * * * *")
    assert "every 15" in result[0]["description"]
    assert "step" in result[0]["description"]


def test_explain_range():
    result = explain("0 9-17 * * *")
    assert "from 9 to 17" in result[1]["description"]


def test_explain_list():
    result = explain("0 0 * * 1,3,5")
    desc = result[4]["description"]
    assert "Monday" in desc
    assert "Wednesday" in desc
    assert "Friday" in desc


def test_explain_month_name():
    result = explain("0 0 1 6 *")
    assert "June" in result[3]["description"]


def test_explain_dow_name():
    result = explain("0 0 * * 0")
    assert "Sunday" in result[4]["description"]


def test_explain_invalid_expression():
    result = explain("not valid")
    assert "error" in result[0]


def test_explain_raw_field_preserved():
    result = explain("5 4 * * *")
    assert result[0]["raw"] == "5"
    assert result[1]["raw"] == "4"


def test_explain_range_with_step():
    desc = _explain_field("1-5/2", 0)
    assert "every 2" in desc
    assert "1-5" in desc
