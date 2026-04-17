"""Parse and validate cron expressions into structured components."""

from dataclasses import dataclass
from typing import Optional

FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]
FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 7),
}

MONTH_ALIASES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

DOW_ALIASES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3,
    "thu": 4, "fri": 5, "sat": 6,
}


@dataclass
class CronExpression:
    minute: str
    hour: str
    day_of_month: str
    month: str
    day_of_week: str

    def __str__(self):
        return f"{self.minute} {self.hour} {self.day_of_month} {self.month} {self.day_of_week}"


class CronParseError(ValueError):
    pass


def _resolve_aliases(value: str, aliases: dict) -> str:
    for alias, num in aliases.items():
        value = value.lower().replace(alias, str(num))
    return value


def _validate_field(value: str, field: str) -> None:
    lo, hi = FIELD_RANGES[field]
    aliases = MONTH_ALIASES if field == "month" else (DOW_ALIASES if field == "day_of_week" else {})
    value = _resolve_aliases(value, aliases)

    if value == "*":
        return

    for part in value.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            if not step.isdigit():
                raise CronParseError(f"Invalid step in field '{field}': {part}")
            part = base
        if "-" in part:
            start, end = part.split("-", 1)
            for v in (start, end):
                if not v.isdigit() or not (lo <= int(v) <= hi):
                    raise CronParseError(f"Value {v} out of range [{lo}-{hi}] in field '{field}'")
        elif part != "*":
            if not part.isdigit() or not (lo <= int(part) <= hi):
                raise CronParseError(f"Value '{part}' out of range [{lo}-{hi}] in field '{field}'")


def parse(expression: str) -> CronExpression:
    """Parse a cron expression string and return a CronExpression."""
    parts = expression.strip().split()
    if len(parts) != 5:
        raise CronParseError(f"Expected 5 fields, got {len(parts)}")

    fields = dict(zip(FIELD_NAMES, parts))
    for name, value in fields.items():
        _validate_field(value, name)

    return CronExpression(**fields)
