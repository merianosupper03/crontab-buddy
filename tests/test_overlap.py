"""Tests for crontab_buddy.overlap."""

import pytest
from datetime import datetime
from crontab_buddy.overlap import detect_overlap, find_all_overlaps, OverlapResult


REF = datetime(2024, 1, 15, 0, 0, 0)


def test_identical_expressions_have_overlap():
    result = detect_overlap("* * * * *", "* * * * *", reference=REF)
    assert bool(result) is True
    assert len(result.overlapping_times) > 0


def test_no_overlap_different_hours():
    # one fires at 6am, other at 7am — no overlap in next hour window
    result = detect_overlap("0 6 * * *", "0 7 * * *", reference=REF, hours=24)
    assert bool(result) is False
    assert result.overlapping_times == []


def test_same_daily_time_overlaps():
    result = detect_overlap("0 12 * * *", "0 12 * * *", reference=REF, hours=24)
    assert bool(result) is True


def test_invalid_expr_a_returns_error():
    result = detect_overlap("bad expr", "* * * * *", reference=REF)
    assert result.error != ""
    assert bool(result) is False


def test_invalid_expr_b_returns_error():
    result = detect_overlap("* * * * *", "not valid", reference=REF)
    assert result.error != ""


def test_str_no_overlap():
    result = detect_overlap("0 6 * * *", "0 7 * * *", reference=REF, hours=24)
    text = str(result)
    assert "No overlap" in text


def test_str_with_overlap():
    result = detect_overlap("0 12 * * *", "0 12 * * *", reference=REF, hours=24)
    text = str(result)
    assert "overlap" in text
    assert "1 time" in text


def test_str_with_error():
    result = OverlapResult("a", "b", error="something went wrong")
    assert "Error" in str(result)


def test_find_all_overlaps_returns_only_overlapping():
    exprs = ["0 6 * * *", "0 7 * * *", "0 6 * * *"]
    results = find_all_overlaps(exprs, reference=REF, hours=24)
    # Only (index 0, index 2) should overlap
    assert len(results) == 1
    assert results[0].expr_a == "0 6 * * *"
    assert results[0].expr_b == "0 6 * * *"


def test_find_all_overlaps_empty_list():
    results = find_all_overlaps([], reference=REF)
    assert results == []


def test_find_all_overlaps_single_expression():
    results = find_all_overlaps(["* * * * *"], reference=REF)
    assert results == []


def test_overlap_result_stores_expressions():
    result = detect_overlap("30 9 * * *", "30 9 * * *", reference=REF, hours=24)
    assert result.expr_a == "30 9 * * *"
    assert result.expr_b == "30 9 * * *"
