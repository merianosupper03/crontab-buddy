import pytest
from crontab_buddy.compare import compare, format_compare


def test_identical_expressions():
    r = compare("0 9 * * 1", "0 9 * * 1")
    assert r["identical"] is True
    assert r["valid_a"] and r["valid_b"]
    assert all(not f["changed"] for f in r["fields"])


def test_single_field_difference():
    r = compare("0 9 * * 1", "0 10 * * 1")
    assert r["identical"] is False
    changed = [f for f in r["fields"] if f["changed"]]
    assert len(changed) == 1
    assert changed[0]["name"] == "hour"
    assert changed[0]["value_a"] == "9"
    assert changed[0]["value_b"] == "10"


def test_multiple_field_differences():
    r = compare("*/5 * * * *", "0 9 1 * 1")
    changed = [f for f in r["fields"] if f["changed"]]
    assert len(changed) >= 2


def test_invalid_expr_a():
    r = compare("bad expression", "0 9 * * 1")
    assert r["valid_a"] is False
    assert r["error_a"] is not None
    assert r["fields"] == []


def test_invalid_expr_b():
    r = compare("0 9 * * 1", "not valid")
    assert r["valid_b"] is False
    assert r["error_b"] is not None


def test_both_invalid():
    r = compare("oops", "also bad")
    assert r["valid_a"] is False
    assert r["valid_b"] is False
    assert r["identical"] is False


def test_descriptions_populated():
    r = compare("0 9 * * 1", "30 18 * * 5")
    assert r["description_a"] is not None
    assert r["description_b"] is not None


def test_format_compare_no_diff():
    r = compare("0 9 * * *", "0 9 * * *")
    out = format_compare(r)
    assert "no differences" in out


def test_format_compare_shows_changed_field():
    r = compare("0 9 * * *", "0 10 * * *")
    out = format_compare(r)
    assert "hour" in out
    assert "->" in out


def test_format_compare_shows_error():
    r = compare("bad", "0 9 * * *")
    out = format_compare(r)
    assert "ERROR" in out
