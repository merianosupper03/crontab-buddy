"""Tests for crontab_buddy.amplitude."""

import pytest
from crontab_buddy.amplitude import (
    assess_amplitude,
    batch_amplitude,
    AmplitudeResult,
    _field_amplitude,
    _grade,
)


def test_returns_amplitude_result():
    r = assess_amplitude("* * * * *")
    assert isinstance(r, AmplitudeResult)


def test_all_wildcards_is_maximal():
    r = assess_amplitude("* * * * *")
    assert r.grade == "maximal"
    assert r.score == pytest.approx(1.0, abs=0.01)


def test_invalid_expression_has_error():
    r = assess_amplitude("bad expr")
    assert r.error is not None
    assert r.grade == "minimal"


def test_single_exact_time_is_low_or_minimal():
    r = assess_amplitude("30 6 1 1 1")
    assert r.grade in ("minimal", "low")
    assert r.score < 0.35


def test_scores_dict_has_five_keys():
    r = assess_amplitude("0 12 * * *")
    assert set(r.scores.keys()) == {"minute", "hour", "dom", "month", "dow"}


def test_field_amplitude_wildcard():
    assert _field_amplitude("*", 60) == 1.0


def test_field_amplitude_list():
    score = _field_amplitude("1,2,3", 60)
    assert pytest.approx(score, abs=0.01) == 3 / 60


def test_field_amplitude_range():
    score = _field_amplitude("0-11", 24)
    assert pytest.approx(score, abs=0.01) == 12 / 24


def test_field_amplitude_step():
    score = _field_amplitude("*/15", 60)
    assert 0.0 < score <= 1.0


def test_field_amplitude_exact_value():
    score = _field_amplitude("5", 60)
    assert pytest.approx(score, abs=0.001) == 1 / 60


def test_grade_maximal():
    assert _grade(0.9) == "maximal"


def test_grade_high():
    assert _grade(0.7) == "high"


def test_grade_moderate():
    assert _grade(0.5) == "moderate"


def test_grade_low():
    assert _grade(0.3) == "low"


def test_grade_minimal():
    assert _grade(0.1) == "minimal"


def test_batch_amplitude_returns_list():
    results = batch_amplitude(["* * * * *", "0 0 * * *"])
    assert len(results) == 2
    assert all(isinstance(r, AmplitudeResult) for r in results)


def test_batch_amplitude_mixed_valid_invalid():
    results = batch_amplitude(["* * * * *", "invalid"])
    assert results[0].error is None
    assert results[1].error is not None


def test_str_with_error():
    r = assess_amplitude("bad")
    assert "error" in str(r)


def test_str_without_error():
    r = assess_amplitude("* * * * *")
    s = str(r)
    assert "score" in s
    assert "grade" in s
