"""Tests for crontab_buddy.texture."""
import pytest
from crontab_buddy.texture import assess_texture, batch_texture, _field_texture, _grade


def test_returns_texture_result():
    result = assess_texture("* * * * *")
    assert result.expression == "* * * * *"
    assert result.score >= 0.0
    assert result.grade != ""


def test_all_wildcards_is_flat_or_plain():
    result = assess_texture("* * * * *")
    assert result.grade in ("flat", "plain")


def test_invalid_expression_has_error():
    result = assess_texture("not valid")
    assert result.error is not None
    assert result.score == 0.0
    assert result.grade == "flat"


def test_plain_integers_score_moderate():
    result = assess_texture("30 6 1 1 1")
    assert result.score >= 0.3


def test_list_fields_raise_score():
    result = assess_texture("0,30 * * * *")
    assert result.score > assess_texture("0 * * * *").score


def test_range_field_raises_score():
    result = assess_texture("0-30 * * * *")
    assert result.score > assess_texture("0 * * * *").score


def test_step_field_raises_score():
    result = assess_texture("*/5 * * * *")
    assert result.score > assess_texture("* * * * *").score


def test_scores_dict_has_five_keys():
    result = assess_texture("*/15 6-18 * * 1-5")
    assert set(result.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_all_scores_between_zero_and_one():
    result = assess_texture("*/15 6-18 1,15 * 1-5")
    for v in result.scores.values():
        assert 0.0 <= v <= 1.0


def test_complex_expression_scores_high():
    result = assess_texture("0,15,30,45 8-18 1-15 */2 1,3,5")
    assert result.score >= 0.5


def test_field_texture_wildcard():
    assert _field_texture("*") == pytest.approx(0.2)


def test_field_texture_plain_integer():
    assert _field_texture("5") == pytest.approx(0.5)


def test_field_texture_list():
    score = _field_texture("1,2,3")
    assert score > 0.2


def test_grade_boundaries():
    assert _grade(0.9) == "rich"
    assert _grade(0.7) == "varied"
    assert _grade(0.5) == "moderate"
    assert _grade(0.3) == "plain"
    assert _grade(0.1) == "flat"


def test_batch_texture_returns_list():
    results = batch_texture(["* * * * *", "0 6 * * 1", "bad expr"])
    assert len(results) == 3


def test_batch_texture_mixed_validity():
    results = batch_texture(["0 6 * * *", "not valid"])
    assert results[0].error is None
    assert results[1].error is not None


def test_str_representation_no_error():
    result = assess_texture("0 6 * * *")
    s = str(result)
    assert "TextureResult" in s
    assert "score" in s


def test_str_representation_with_error():
    result = assess_texture("bad")
    s = str(result)
    assert "error" in s
