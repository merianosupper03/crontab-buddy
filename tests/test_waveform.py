import pytest
from crontab_buddy.waveform import assess_waveform, WaveformResult


def test_returns_waveform_result():
    result = assess_waveform("* * * * *")
    assert isinstance(result, WaveformResult)


def test_every_minute_has_no_error():
    result = assess_waveform("* * * * *")
    assert result.error is None


def test_every_minute_fires_1440():
    result = assess_waveform("* * * * *")
    assert result.firing_count == 1440


def test_every_minute_is_sinusoidal_or_pulsed():
    result = assess_waveform("* * * * *")
    assert result.label in ("sinusoidal", "pulsed")


def test_every_minute_score_near_one():
    result = assess_waveform("* * * * *")
    assert result.score >= 0.8


def test_daily_midnight_fires_once():
    result = assess_waveform("0 0 * * *")
    assert result.firing_count == 1


def test_daily_midnight_peak_hour_is_zero():
    result = assess_waveform("0 0 * * *")
    assert result.peak_hour == 0


def test_daily_midnight_label_is_flat_or_sporadic():
    result = assess_waveform("0 0 * * *")
    assert result.label in ("flat", "sporadic")


def test_hourly_fires_24_times():
    result = assess_waveform("0 * * * *")
    assert result.firing_count == 24


def test_hourly_score_is_high():
    result = assess_waveform("0 * * * *")
    assert result.score >= 0.7


def test_step_every_15_minutes_fires_96():
    result = assess_waveform("*/15 * * * *")
    assert result.firing_count == 96


def test_specific_hour_range_fires_correctly():
    result = assess_waveform("0 9-17 * * *")
    assert result.firing_count == 9


def test_invalid_expression_has_error():
    result = assess_waveform("bad expression")
    assert result.error is not None


def test_invalid_expression_firing_count_zero():
    result = assess_waveform("bad expression")
    assert result.firing_count == 0


def test_invalid_expression_label_is_flat():
    result = assess_waveform("bad expression")
    assert result.label == "flat"


def test_str_representation_contains_expression():
    result = assess_waveform("0 12 * * *")
    assert "0 12 * * *" in str(result)


def test_peak_hour_within_valid_range():
    result = assess_waveform("30 14 * * *")
    assert result.peak_hour == 14


def test_list_hours_fires_at_correct_count():
    result = assess_waveform("0 6,12,18 * * *")
    assert result.firing_count == 3
