"""Tests for crontab_buddy/rating.py"""

import pytest
from crontab_buddy import rating


@pytest.fixture
def tmp_rating(tmp_path):
    return str(tmp_path / "ratings.json")


def test_rate_and_get(tmp_rating):
    rating.rate_expression("0 * * * *", 4, tmp_rating)
    assert rating.get_rating("0 * * * *", tmp_rating) == 4


def test_get_missing_returns_none(tmp_rating):
    assert rating.get_rating("* * * * *", tmp_rating) is None


def test_overwrite_rating(tmp_rating):
    rating.rate_expression("0 0 * * *", 3, tmp_rating)
    rating.rate_expression("0 0 * * *", 5, tmp_rating)
    assert rating.get_rating("0 0 * * *", tmp_rating) == 5


def test_invalid_score_raises(tmp_rating):
    with pytest.raises(ValueError):
        rating.rate_expression("* * * * *", 0, tmp_rating)
    with pytest.raises(ValueError):
        rating.rate_expression("* * * * *", 6, tmp_rating)


def test_delete_existing(tmp_rating):
    rating.rate_expression("0 12 * * *", 5, tmp_rating)
    result = rating.delete_rating("0 12 * * *", tmp_rating)
    assert result is True
    assert rating.get_rating("0 12 * * *", tmp_rating) is None


def test_delete_missing_returns_false(tmp_rating):
    assert rating.delete_rating("0 0 1 1 *", tmp_rating) is False


def test_list_ratings_sorted(tmp_rating):
    rating.rate_expression("* * * * *", 2, tmp_rating)
    rating.rate_expression("0 * * * *", 5, tmp_rating)
    rating.rate_expression("0 0 * * *", 3, tmp_rating)
    result = list_r = list(rating.list_ratings(tmp_rating).values())
    assert list_r == sorted(list_r, reverse=True)


def test_top_rated_limits(tmp_rating):
    for i, expr in enumerate(["* * * * *", "0 * * * *", "0 0 * * *"], start=3):
        rating.rate_expression(expr, i, tmp_rating)
    top = rating.top_rated(2, tmp_rating)
    assert len(top) == 2
