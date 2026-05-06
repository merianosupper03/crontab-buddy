"""compliance.py — check cron expressions against policy rules."""

from dataclasses import dataclass, field
from typing import List, Optional

from crontab_buddy.parser import CronExpression, CronParseError
from crontab_buddy.recurrence import recurrence_interval_seconds

# Built-in policy rules
_POLICIES = {
    "no_every_minute": "Expression must not run every minute",
    "no_every_hour": "Expression must not run more than once per hour",
    "business_hours_only": "Expression must only run between 06:00 and 22:00",
    "weekdays_only": "Expression must not run on weekends (Sat/Sun)",
}


@dataclass
class ComplianceResult:
    expression: str
    passed: bool
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.passed

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        lines = [f"[{status}] {self.expression}"]
        for v in self.violations:
            lines.append(f"  VIOLATION: {v}")
        for w in self.warnings:
            lines.append(f"  WARNING: {w}")
        return "\n".join(lines)


def list_policies() -> dict:
    """Return all available policy names and their descriptions."""
    return dict(_POLICIES)


def check_compliance(
    expression: str,
    policies: Optional[List[str]] = None,
) -> ComplianceResult:
    """Check a cron expression against the given policies (or all by default)."""
    active = policies if policies is not None else list(_POLICIES.keys())
    violations: List[str] = []
    warnings: List[str] = []

    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return ComplianceResult(
            expression=expression,
            passed=False,
            violations=[f"Invalid expression: {exc}"],
        )

    interval = recurrence_interval_seconds(expression)

    if "no_every_minute" in active and interval is not None and interval < 60:
        violations.append(_POLICIES["no_every_minute"])

    if "no_every_hour" in active and interval is not None and interval < 3600:
        if interval >= 60:  # already caught above if < 60
            warnings.append("Expression runs more than once per hour")
        elif interval < 60:
            pass  # already a violation

    if "business_hours_only" in active:
        hour_field = expr.fields[1]
        if hour_field == "*":
            violations.append(_POLICIES["business_hours_only"])
        else:
            try:
                hours = [int(h) for h in hour_field.split(",") if h.isdigit()]
                if any(h < 6 or h > 22 for h in hours):
                    violations.append(_POLICIES["business_hours_only"])
            except ValueError:
                warnings.append("Could not fully evaluate business_hours_only policy")

    if "weekdays_only" in active:
        dow_field = expr.fields[4]
        if dow_field in ("*", "?"):
            violations.append(_POLICIES["weekdays_only"])
        else:
            parts = dow_field.replace("-", ",").split(",")
            weekend = {"0", "6", "7", "sun", "sat"}
            if any(p.lower() in weekend for p in parts):
                violations.append(_POLICIES["weekdays_only"])

    return ComplianceResult(
        expression=expression,
        passed=len(violations) == 0,
        violations=violations,
        warnings=warnings,
    )
