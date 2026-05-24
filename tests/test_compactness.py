import pytest
from crontab_buddy.compactness import assess_compactness, batch_compactness, CompactnessResult


def test_returns_compactness_result():
    result = assess_compactness("* * * * *")
    assert isinstance(result, CompactnessResult)


def test_invalid_expression_has_error():
    result = assess_compactness("bad expr")
    assert result.error is not None
    assert result.score == 0.0


def test_all_wildcards_is_terse():
    result = assess_compactness("* * * * *")
    assert result.grade == "terse"
    assert result.score >= 0.85


def test_single_exact_time_is_verbose_or_lower():
    result = assess_compactness("30 9 15 6 1")
    assert result.grade in ("verbose", "exhaustive")
    assert result.score < 0.45


def test_scores_dict_has_five_keys():
    result = assess_compactness("0 12 * * *")
    assert set(result.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 0 * * *", "*/5 * * * *", "1,2,3 * * * *"]:
        result = assess_compactness(expr)
        assert 0.0 <= result.score <= 1.0


def test_step_expression_is_compact():
    result = assess_compactness("*/15 * * * *")
    assert result.grade in ("terse", "compact")


def test_list_expression_lowers_score():
    wildcard = assess_compactness("* * * * *")
    listed = assess_compactness("1,2,3,4,5 * * * *")
    assert listed.score < wildcard.score


def test_range_expression_moderate():
    result = assess_compactness("0-30 * * * *")
    field_score = result.scores["minute"]
    assert field_score == pytest.approx(0.4)


def test_str_no_error():
    result = assess_compactness("0 0 * * *")
    s = str(result)
    assert "CompactnessResult" in s
    assert "error" not in s


def test_str_with_error():
    result = assess_compactness("not valid")
    s = str(result)
    assert "error=" in s


def test_batch_compactness_returns_list():
    results = batch_compactness(["* * * * *", "0 0 * * *", "bad"])
    assert len(results) == 3
    assert all(isinstance(r, CompactnessResult) for r in results)


def test_batch_compactness_invalid_has_error():
    results = batch_compactness(["bad expr"])
    assert results[0].error is not None
