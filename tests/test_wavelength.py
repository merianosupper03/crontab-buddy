"""Tests for crontab_buddy.wavelength."""
import pytest
from crontab_buddy.wavelength import assess_wavelength, batch_wavelength, WavelengthResult


def test_returns_wavelength_result():
    result = assess_wavelength("* * * * *")
    assert isinstance(result, WavelengthResult)


def test_invalid_expression_has_error():
    result = assess_wavelength("bad expr")
    assert result.error is not None
    assert result.label == "unknown"


def test_every_minute_period_is_60():
    result = assess_wavelength("* * * * *")
    assert result.error is None
    assert result.period_seconds == pytest.approx(60.0)


def test_every_minute_is_instantaneous_or_ultra_short():
    result = assess_wavelength("* * * * *")
    assert result.label in ("instantaneous", "ultra-short")


def test_every_minute_score_near_zero():
    result = assess_wavelength("* * * * *")
    assert result.score < 0.01


def test_hourly_period_is_3600():
    result = assess_wavelength("0 * * * *")
    assert result.error is None
    assert result.period_seconds == pytest.approx(3600.0)


def test_daily_period_is_86400():
    result = assess_wavelength("0 0 * * *")
    assert result.error is None
    assert result.period_seconds == pytest.approx(86400.0)


def test_weekly_period_is_604800():
    result = assess_wavelength("0 0 * * 0")
    assert result.error is None
    assert result.period_seconds == pytest.approx(604800.0)


def test_weekly_score_is_one():
    result = assess_wavelength("0 0 * * 0")
    assert result.score == pytest.approx(1.0)


def test_weekly_label_is_extended():
    result = assess_wavelength("0 0 * * 0")
    assert result.label == "extended"


def test_score_between_zero_and_one():
    for expr in ["* * * * *", "0 * * * *", "0 0 * * *", "0 0 * * 0"]:
        r = assess_wavelength(expr)
        if not r.error:
            assert 0.0 <= r.score <= 1.0


def test_batch_returns_list():
    results = batch_wavelength(["* * * * *", "0 * * * *"])
    assert len(results) == 2
    assert all(isinstance(r, WavelengthResult) for r in results)


def test_batch_handles_invalid():
    results = batch_wavelength(["* * * * *", "not valid"])
    assert results[0].error is None
    assert results[1].error is not None


def test_str_no_error():
    r = assess_wavelength("0 * * * *")
    s = str(r)
    assert "period_seconds" in s


def test_str_with_error():
    r = assess_wavelength("bad")
    s = str(r)
    assert "error" in s
