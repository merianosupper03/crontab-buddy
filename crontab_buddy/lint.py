"""Lint cron expressions for common mistakes and anti-patterns."""

from dataclasses import dataclass, field
from typing import List
from crontab_buddy.parser import CronExpression, CronParseError


@dataclass
class LintResult:
    warnings: List[str] = field(default_factory=list)
    hints: List[str] = field(default_factory=list)

    def ok(self) -> bool:
        return len(self.warnings) == 0

    def __str__(self) -> str:
        lines = []
        for w in self.warnings:
            lines.append(f"[WARN]  {w}")
        for h in self.hints:
            lines.append(f"[HINT]  {h}")
        return "\n".join(lines) if lines else "No issues found."


def lint(expression: str) -> LintResult:
    result = LintResult()

    try:
        expr = CronExpression(expression)
    except CronParseError as e:
        result.warnings.append(f"Invalid expression: {e}")
        return result

    minute, hour, dom, month, dow = (
        expr.minute, expr.hour, expr.dom, expr.month, expr.dow
    )

    # Warn about running every minute
    if minute == "*" and hour == "*":
        result.warnings.append(
            "Expression runs every minute — this is rarely intentional."
        )

    # Hint about both dom and dow being set
    if dom != "*" and dow != "*":
        result.hints.append(
            "Both day-of-month and day-of-week are set; cron uses OR logic between them."
        )

    # Warn about step of 1 (redundant)
    for label, val in [("minute", minute), ("hour", hour), ("dom", dom), ("month", month), ("dow", dow)]:
        if "/1" in val:
            result.warnings.append(
                f"Step '/1' in {label} field is redundant — use '*' instead."
            )

    # Hint about midnight shorthand
    if minute == "0" and hour == "0":
        result.hints.append(
            "Runs at midnight. Consider using '@daily' alias for clarity."
        )

    # Warn about large step values that may never align well
    for label, val in [("minute", minute), ("hour", hour)]:
        if val.startswith("*/"):
            try:
                step = int(val.split("/")[1])
                if label == "minute" and step > 30:
                    result.warnings.append(
                        f"Minute step of {step} means the job runs only once or twice per hour."
                    )
                if label == "hour" and step > 12:
                    result.warnings.append(
                        f"Hour step of {step} means the job runs only once per day."
                    )
            except ValueError:
                pass

    return result
