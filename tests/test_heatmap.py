"""Tests for crontab_buddy.heatmap."""

import pytest
from crontab_buddy.heatmap import (
    build_heatmap,
    format_heatmap,
    summary_heatmap,
    DAYS,
    HOURS,
)


def test_build_heatmap_returns_all_days():
    hm = build_heatmap([])
    assert set(hm.keys()) == set(DAYS)


def test_build_heatmap_returns_all_hours():
    hm = build_heatmap([])
    for day in DAYS:
        assert set(hm[day].keys()) == set(HOURS)


def test_empty_expressions_all_zeros():
    hm = build_heatmap([])
    for day in DAYS:
        assert all(v == 0 for v in hm[day].values())


def test_every_minute_every_hour_increments_all():
    # "* * * * *" matches every hour every day
    hm = build_heatmap(["* * * * *"])
    for day in DAYS:
        for h in HOURS:
            assert hm[day][h] == 1


def test_specific_hour_only_increments_that_hour():
    # runs at 9am every day
    hm = build_heatmap(["0 9 * * *"])
    for day in DAYS:
        assert hm[day][9] == 1
        assert hm[day][8] == 0
        assert hm[day][10] == 0


def test_specific_dow_only_increments_that_day():
    # runs every hour on Monday (dow=1)
    hm = build_heatmap(["0 * * * 1"])
    for h in HOURS:
        assert hm["Mon"][h] == 1
    for day in ["Sun", "Tue", "Wed", "Thu", "Fri", "Sat"]:
        assert all(v == 0 for v in hm[day].values())


def test_invalid_expression_is_skipped():
    hm = build_heatmap(["not a cron"])
    for day in DAYS:
        assert all(v == 0 for v in hm[day].values())


def test_multiple_expressions_accumulate():
    # 9am and 10am every day
    hm = build_heatmap(["0 9 * * *", "0 10 * * *"])
    for day in DAYS:
        assert hm[day][9] == 1
        assert hm[day][10] == 1
        assert hm[day][11] == 0


def test_format_heatmap_contains_day_names():
    hm = build_heatmap([])
    output = format_heatmap(hm)
    for day in DAYS:
        assert day in output


def test_format_heatmap_contains_hour_header():
    hm = build_heatmap([])
    output = format_heatmap(hm)
    assert "0" in output
    assert "23" in output


def test_summary_heatmap_keys_are_days():
    hm = build_heatmap([])
    s = summary_heatmap(hm)
    assert set(s.keys()) == set(DAYS)


def test_summary_heatmap_totals_correctly():
    # every hour on Monday only
    hm = build_heatmap(["0 * * * 1"])
    s = summary_heatmap(hm)
    assert s["Mon"] == 24
    assert s["Sun"] == 0
