"""Tests for crontab_buddy.rhythm."""

import pytest

from crontab_buddy.rhythm import (
    RhythmResult,
    assess_rhythm,
    batch_rhythm,
    _grade,
)


def test_returns_rhythm_result():
    result = assess_rhythm("* * * * *")
    assert isinstance(result, RhythmResult)


def test_every_minute_is_metronomic():
    result = assess_rhythm("* * * * *")
    assert result.level == "metronomic"
    assert result.error is None


def test_every_minute_score_near_one():
    result = assess_rhythm("* * * * *")
    assert result.score >= 0.9


def test_every_minute_has_uniform_intervals():
    result = assess_rhythm("* * * * *")
    assert all(i == 1 for i in result.intervals)


def test_single_firing_has_no_intervals():
    result = assess_rhythm("30 6 * * *")
    assert result.intervals == []


def test_single_firing_score_is_one():
    result = assess_rhythm("30 6 * * *")
    assert result.score == 1.0


def test_invalid_expression_has_error():
    result = assess_rhythm("bad expression")
    assert result.error is not None
    assert result.score == 0.0


def test_invalid_expression_level_is_chaotic():
    result = assess_rhythm("bad expression")
    assert result.level == "chaotic"


def test_step_every_15_minutes_is_metronomic():
    result = assess_rhythm("*/15 * * * *")
    assert result.level in ("metronomic", "steady")
    assert result.score >= 0.7


def test_step_every_15_has_uniform_intervals():
    result = assess_rhythm("*/15 * * * *")
    assert len(set(result.intervals)) == 1


def test_batch_rhythm_returns_list():
    results = batch_rhythm(["* * * * *", "0 6 * * *"])
    assert len(results) == 2
    assert all(isinstance(r, RhythmResult) for r in results)


def test_batch_rhythm_invalid_included():
    results = batch_rhythm(["* * * * *", "not valid"])
    errors = [r for r in results if r.error]
    assert len(errors) == 1


def test_grade_metronomic():
    assert _grade(0.95) == "metronomic"


def test_grade_steady():
    assert _grade(0.75) == "steady"


def test_grade_irregular():
    assert _grade(0.55) == "irregular"


def test_grade_erratic():
    assert _grade(0.3) == "erratic"


def test_grade_chaotic():
    assert _grade(0.1) == "chaotic"


def test_str_no_error():
    r = assess_rhythm("*/30 * * * *")
    s = str(r)
    assert "RhythmResult" in s
    assert "level=" in s


def test_str_with_error():
    r = assess_rhythm("invalid")
    s = str(r)
    assert "error=" in s
