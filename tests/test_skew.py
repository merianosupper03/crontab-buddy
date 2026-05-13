"""Tests for crontab_buddy.skew."""
import pytest
from crontab_buddy.skew import assess_skew, batch_skew, SkewResult


def test_returns_skew_result():
    result = assess_skew("0 12 * * *")
    assert isinstance(result, SkewResult)


def test_invalid_expression_has_error():
    result = assess_skew("not valid")
    assert result.error is not None
    assert result.score == 1.0


def test_noon_is_balanced_or_slight():
    # fires exactly at noon — right on the boundary, so 100% AM
    result = assess_skew("0 12 * * *")
    assert result.error is None
    # noon (minute 720) counts as afternoon (>= 720)
    assert result.afternoon_share == pytest.approx(1.0)
    assert result.morning_share == pytest.approx(0.0)


def test_midnight_is_fully_morning_skewed():
    result = assess_skew("0 0 * * *")
    assert result.error is None
    assert result.morning_share == pytest.approx(1.0)
    assert result.afternoon_share == pytest.approx(0.0)
    assert result.score == pytest.approx(1.0)


def test_every_minute_is_balanced():
    result = assess_skew("* * * * *")
    assert result.error is None
    # 720 morning minutes, 720 afternoon minutes
    assert result.morning_share == pytest.approx(0.5)
    assert result.afternoon_share == pytest.approx(0.5)
    assert result.score == pytest.approx(0.0, abs=0.01)
    assert result.label == "balanced"


def test_score_between_zero_and_one():
    for expr in ["*/5 * * * *", "0 9 * * 1", "30 14 * * *", "0 6 * * *"]:
        r = assess_skew(expr)
        if not r.error:
            assert 0.0 <= r.score <= 1.0


def test_morning_only_expression():
    # fires every hour from 0 to 5 — all morning
    result = assess_skew("0 0-5 * * *")
    assert result.error is None
    assert result.morning_share == pytest.approx(1.0)
    assert result.score == pytest.approx(1.0)
    assert result.label in ("heavy", "extreme")


def test_afternoon_only_expression():
    result = assess_skew("0 12-23 * * *")
    assert result.error is None
    assert result.afternoon_share == pytest.approx(1.0)
    assert result.score == pytest.approx(1.0)


def test_label_balanced():
    result = assess_skew("* * * * *")
    assert result.label == "balanced"


def test_label_extreme():
    result = assess_skew("0 0 * * *")
    assert result.label == "extreme"


def test_batch_skew_returns_list():
    results = batch_skew(["* * * * *", "0 0 * * *", "bad expr"])
    assert len(results) == 3
    assert all(isinstance(r, SkewResult) for r in results)


def test_batch_skew_preserves_order():
    exprs = ["0 6 * * *", "0 18 * * *"]
    results = batch_skew(exprs)
    assert results[0].expression == exprs[0]
    assert results[1].expression == exprs[1]


def test_str_representation_no_error():
    result = assess_skew("* * * * *")
    s = str(result)
    assert "balanced" in s
    assert "score=" in s


def test_str_representation_with_error():
    result = assess_skew("bad")
    s = str(result)
    assert "error" in s
