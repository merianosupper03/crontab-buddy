"""Waveform analysis: describe the firing pattern of a cron expression
as a repeating waveform over a 24-hour window."""

from dataclasses import dataclass, field
from typing import List, Optional
from crontab_buddy.parser import CronExpression, CronParseError


_GRADES = [
    (0.9, "sinusoidal"),
    (0.7, "pulsed"),
    (0.5, "irregular"),
    (0.3, "sporadic"),
    (0.0, "flat"),
]


def _grade(score: float) -> str:
    for threshold, label in _GRADES:
        if score >= threshold:
            return label
    return "flat"


def _firing_minutes(expr: CronExpression) -> List[int]:
    """Return sorted list of minutes-of-day that the expression fires in one day."""
    minutes_field = expr.fields[0]
    hours_field = expr.fields[1]

    def expand(field_val, max_val):
        if field_val == "*":
            return list(range(max_val))
        if "/" in field_val:
            base, step = field_val.split("/", 1)
            start = 0 if base == "*" else int(base)
            return list(range(start, max_val, int(step)))
        if "-" in field_val:
            lo, hi = field_val.split("-", 1)
            return list(range(int(lo), int(hi) + 1))
        if "," in field_val:
            return [int(v) for v in field_val.split(",")]
        return [int(field_val)]

    minutes = expand(minutes_field, 60)
    hours = expand(hours_field, 24)
    result = sorted(set(h * 60 + m for h in hours for m in minutes))
    return result


@dataclass
class WaveformResult:
    expression: str
    firing_count: int
    peak_hour: Optional[int]
    trough_hour: Optional[int]
    score: float
    label: str
    error: Optional[str] = None

    def __str__(self):
        if self.error:
            return f"Waveform({self.expression}): error={self.error}"
        return (
            f"Waveform({self.expression}): {self.label} "
            f"score={self.score:.3f} fires={self.firing_count}/day "
            f"peak_hour={self.peak_hour} trough_hour={self.trough_hour}"
        )


def assess_waveform(expression: str) -> WaveformResult:
    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return WaveformResult(
            expression=expression,
            firing_count=0,
            peak_hour=None,
            trough_hour=None,
            score=0.0,
            label="flat",
            error=str(exc),
        )

    firings = _firing_minutes(expr)
    if not firings:
        return WaveformResult(
            expression=expression,
            firing_count=0,
            peak_hour=None,
            trough_hour=None,
            score=0.0,
            label="flat",
        )

    hourly = [0] * 24
    for m in firings:
        hourly[m // 60] += 1

    peak_hour = hourly.index(max(hourly))
    non_zero = [h for h in hourly if h > 0]
    trough_hour = hourly.index(min(non_zero)) if non_zero else None

    spread = len([h for h in hourly if h > 0]) / 24.0
    max_h = max(hourly)
    min_h = min(non_zero) if non_zero else 0
    evenness = (min_h / max_h) if max_h > 0 else 0.0
    score = round((spread + evenness) / 2.0, 4)
    label = _grade(score)

    return WaveformResult(
        expression=expression,
        firing_count=len(firings),
        peak_hour=peak_hour,
        trough_hour=trough_hour,
        score=score,
        label=label,
    )
