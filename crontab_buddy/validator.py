"""Extended validation with detailed diagnostics for cron expressions."""

from dataclasses import dataclass, field
from typing import List
from .parser import CronExpression, CronParseError


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __bool__(self):
        return self.valid


FIELD_NAMES = ["minute", "hour", "day-of-month", "month", "day-of-week"]

_SUSPICIOUS_PATTERNS = [
    ("* * * * *", "runs every minute — is that intentional?"),
    ("0 * * * *", "runs every hour"),
]


def validate(expression: str) -> ValidationResult:
    """Parse and validate a cron expression, returning a ValidationResult."""
    errors: List[str] = []
    warnings: List[str] = []

    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return ValidationResult(valid=False, errors=[str(exc)])

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    for name, value in zip(FIELD_NAMES, fields):
        if value == "**":
            errors.append(f"Field '{name}' contains '**' which is invalid.")

    dom_wildcard = expr.dom == "*"
    dow_wildcard = expr.dow == "*"
    if not dom_wildcard and not dow_wildcard:
        warnings.append(
            "Both day-of-month and day-of-week are set; "
            "cron treats this as OR — may run more often than expected."
        )

    for pattern, msg in _SUSPICIOUS_PATTERNS:
        if expression.strip() == pattern:
            warnings.append(msg)

    return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
