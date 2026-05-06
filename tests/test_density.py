"""Tests for crontab_buddy/density.py"""

import pytest
from crontab_buddy.density import compute_density, WINDOWS, DensityResult


def test_windows_contains_expected_keys():
    assert "1h" in WINDOWS
    assert "24h" in WINDOWS
    assert "7d" in WINDOWS
    assert "30d" in WINDOWS


def test_every_minute_24h_fires_1440():
    result = compute_density("* * * * *", "24h")
    assert result.fires == 1440


def test_every_minute_1h_fires_60():
    result = compute_density("* * * * *", "1h")
    assert result.fires == 60


def test_hourly_24h_fires_24():
    result = compute_density("0 * * * *", "24h")
    assert result.fires == 24


def test_daily_midnight_24h_fires_1():
    result = compute_density("0 0 * * *", "24h")
    assert result.fires == 1


def test_every_minute_ratio_is_one():
    result = compute_density("* * * * *", "24h")
    assert abs(result.ratio - 1.0) < 1e-6


def test_daily_ratio_is_low():
    result = compute_density("0 0 * * *", "24h")
    assert result.ratio < 0.01


def test_every_minute_label_is_very_high():
    result = compute_density("* * * * *", "24h")
    assert result.label == "very high"


def test_daily_label_is_sparse():
    result = compute_density("0 0 * * *", "24h")
    assert result.label == "sparse"


def test_invalid_expression_fires_zero():
    result = compute_density("not a cron", "24h")
    assert result.fires == 0
    assert result.label == "invalid"
    assert result.ratio == 0.0


def test_unknown_window_raises():
    with pytest.raises(ValueError, match="Unknown window"):
        compute_density("* * * * *", "99y")


def test_result_is_density_result_instance():
    result = compute_density("0 * * * *", "1h")
    assert isinstance(result, DensityResult)


def test_str_contains_expression():
    result = compute_density("0 12 * * *", "24h")
    s = str(result)
    assert "0 12 * * *" in s


def test_str_contains_window():
    result = compute_density("0 12 * * *", "24h")
    s = str(result)
    assert "24h" in s


def test_step_every_two_minutes_fires_720():
    result = compute_density("*/2 * * * *", "24h")
    assert result.fires == 720
