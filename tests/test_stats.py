"""Tests for crontab_buddy/stats.py"""

import pytest
from unittest.mock import patch

from crontab_buddy.stats import expression_frequency, field_distribution, summary

FAKE_HISTORY = [
    "* * * * *",
    "0 9 * * 1",
    "* * * * *",
    "0 9 * * 1",
    "* * * * *",
    "30 6 * * *",
]


@pytest.fixture(autouse=True)
def mock_history():
    with patch("crontab_buddy.stats.get_history", return_value=FAKE_HISTORY):
        yield


def test_expression_frequency_order():
    freq = expression_frequency()
    assert freq[0]["expression"] == "* * * * *"
    assert freq[0]["count"] == 3


def test_expression_frequency_all_present():
    freq = expression_frequency()
    exprs = [f["expression"] for f in freq]
    assert "0 9 * * 1" in exprs
    assert "30 6 * * *" in exprs


def test_expression_frequency_has_description():
    freq = expression_frequency()
    for item in freq:
        assert "description" in item
        assert isinstance(item["description"], str)


def test_field_distribution_keys():
    dist = field_distribution()
    assert set(dist.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_field_distribution_minute_counts():
    dist = field_distribution()
    # "* * * * *" x3, "30 6 * * *" x1 => minute "*" appears 4 times, "0" twice, "30" once
    assert dist["minute"]["*"] == 4
    assert dist["minute"]["0"] == 2
    assert dist["minute"]["30"] == 1


def test_summary_total_entries():
    s = summary()
    assert s["total_entries"] == 6


def test_summary_unique_expressions():
    s = summary()
    assert s["unique_expressions"] == 3


def test_summary_most_used():
    s = summary()
    assert s["most_used"] is not None
    assert s["most_used"]["expression"] == "* * * * *"
    assert s["most_used"]["count"] == 3


def test_summary_empty_history():
    with patch("crontab_buddy.stats.get_history", return_value=[]):
        s = summary()
    assert s["total_entries"] == 0
    assert s["unique_expressions"] == 0
    assert s["most_used"] is None
