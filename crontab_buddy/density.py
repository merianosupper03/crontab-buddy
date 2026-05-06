"""density.py — compute how densely a cron expression fires within a time window."""

from typing import Dict
from crontab_buddy.parser import CronExpression, CronParseError


WINDOWS: Dict[str, int] = {
    "1h": 60,
    "24h": 1440,
    "7d": 10080,
    "30d": 43200,
}


class DensityResult:
    def __init__(self, expression: str, window: str, fires: int, minutes: int, ratio: float, label: str):
        self.expression = expression
        self.window = window
        self.fires = fires
        self.minutes = minutes
        self.ratio = ratio
        self.label = label

    def __str__(self) -> str:
        return (
            f"Expression : {self.expression}\n"
            f"Window     : {self.window}\n"
            f"Fires      : {self.fires} / {self.minutes} minutes\n"
            f"Ratio      : {self.ratio:.4f}\n"
            f"Density    : {self.label}"
        )


def _label(ratio: float) -> str:
    if ratio >= 0.5:
        return "very high"
    if ratio >= 0.1:
        return "high"
    if ratio >= 0.01:
        return "moderate"
    if ratio >= 0.001:
        return "low"
    return "sparse"


def _safe_parse(expression: str):
    try:
        return CronExpression(expression)
    except CronParseError:
        return None


def _matches(expr: CronExpression, minute: int, hour: int) -> bool:
    from crontab_buddy.scheduler import _matches_field
    return (
        _matches_field(expr.minute, minute, 0, 59)
        and _matches_field(expr.hour, hour, 0, 23)
    )


def compute_density(expression: str, window: str = "24h") -> DensityResult:
    if window not in WINDOWS:
        raise ValueError(f"Unknown window '{window}'. Choose from: {list(WINDOWS.keys())}")

    minutes = WINDOWS[window]
    expr = _safe_parse(expression)

    if expr is None:
        return DensityResult(expression, window, 0, minutes, 0.0, "invalid")

    fires = 0
    for m in range(minutes):
        hour = (m // 60) % 24
        minute = m % 60
        if _matches(expr, minute, hour):
            fires += 1

    ratio = fires / minutes if minutes > 0 else 0.0
    return DensityResult(expression, window, fires, minutes, ratio, _label(ratio))


def format_density(result: DensityResult) -> str:
    return str(result)
