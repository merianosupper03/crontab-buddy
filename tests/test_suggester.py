"""Tests for crontab_buddy.suggester."""

import pytest
from crontab_buddy.suggester import suggest, list_all


def test_suggest_exact_keyword():
    results = suggest("hourly")
    assert len(results) >= 1
    exprs = [r[0] for r in results]
    assert "0 * * * *" in exprs


def test_suggest_partial_match():
    results = suggest("daily")
    exprs = [r[0] for r in results]
    assert "0 0 * * *" in exprs


def test_suggest_case_insensitive():
    results = suggest("HOURLY")
    exprs = [r[0] for r in results]
    assert "0 * * * *" in exprs


def test_suggest_no_match_returns_empty():
    results = suggest("xyzzy foobar nonsense")
    assert results == []


def test_suggest_max_results():
    results = suggest("every", max_results=3)
    assert len(results) <= 3


def test_suggest_returns_tuples_of_two():
    results = suggest("daily")
    for item in results:
        assert isinstance(item, tuple)
        assert len(item) == 2


def test_suggest_no_duplicates():
    results = suggest("every")
    exprs = [r[0] for r in results]
    assert len(exprs) == len(set(exprs))


def test_list_all_returns_all():
    all_suggestions = list_all()
    assert len(all_suggestions) >= 10


def test_list_all_structure():
    for expr, label in list_all():
        assert isinstance(expr, str)
        assert isinstance(label, str)
        assert len(expr.split()) == 5


def test_suggest_weekday():
    results = suggest("weekday")
    exprs = [r[0] for r in results]
    assert "0 9 * * 1-5" in exprs
