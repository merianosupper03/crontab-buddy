"""Tests for crontab_buddy.contrast."""
import pytest
from crontab_buddy.contrast import assess_contrast, ContrastResult


def test_returns_contrast_result():
    result = assess_contrast("0 9 * * *", [])
    assert isinstance(result, ContrastResult)


def test_invalid_expression_has_error():
    result = assess_contrast("bad expr", [])
    assert result.error is not None
    assert result.score == 0.0


def test_no_peers_is_fully_vivid():
    result = assess_contrast("0 9 * * *", [])
    assert result.error is None
    assert result.score == 1.0
    assert result.grade == "vivid"


def test_identical_peer_is_indistinct():
    result = assess_contrast("0 9 * * *", ["0 9 * * *"])
    assert result.error is None
    assert result.score == 0.0
    assert result.grade == "indistinct"


def test_non_overlapping_peer_is_vivid():
    result = assess_contrast("0 9 * * *", ["0 22 * * *"])
    assert result.error is None
    assert result.score == 1.0


def test_partial_overlap_reduces_score():
    # every minute fires 1440 slots; peer fires at hour 9 (60 slots)
    result = assess_contrast("* * * * *", ["* 9 * * *"])
    assert result.error is None
    assert 0.0 < result.score < 1.0


def test_shared_minutes_counted_correctly():
    # expression fires at 09:00 only; peer also fires at 09:00
    result = assess_contrast("0 9 * * *", ["0 9 * * *"])
    assert result.shared_minutes == 1
    assert result.total_minutes == 1


def test_total_minutes_every_minute():
    result = assess_contrast("* * * * *", [])
    assert result.total_minutes == 1440


def test_invalid_peer_is_ignored():
    # invalid peer should not crash; expression vs no valid peers => score 1.0
    result = assess_contrast("0 9 * * *", ["not valid", "also bad"])
    assert result.error is None
    assert result.score == 1.0


def test_grade_vivid():
    result = assess_contrast("0 9 * * *", [])
    assert result.grade == "vivid"


def test_grade_indistinct():
    result = assess_contrast("0 9 * * *", ["0 9 * * *"])
    assert result.grade == "indistinct"


def test_str_no_error():
    result = assess_contrast("0 9 * * *", [])
    s = str(result)
    assert "vivid" in s
    assert "0 9 * * *" in s


def test_str_with_error():
    result = assess_contrast("bad", [])
    s = str(result)
    assert "error" in s.lower()


def test_multiple_peers_union():
    # expression fires at 09:00; peers cover 09:00 and 10:00
    result = assess_contrast("0 9 * * *", ["0 9 * * *", "0 10 * * *"])
    assert result.shared_minutes == 1
    assert result.score == 0.0
