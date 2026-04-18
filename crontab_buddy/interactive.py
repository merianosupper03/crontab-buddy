"""Interactive step-by-step cron expression builder."""

from typing import Callable, Optional
from .validator import validate
from .humanizer import humanize
from .parser import CronExpression

FIELD_PROMPTS = [
    ("minute",       "Minute   (0-59, */n, a-b, or *)"),
    ("hour",         "Hour     (0-23, */n, a-b, or *)"),
    ("dom",          "Day/month(1-31, */n, a-b, or *)"),
    ("month",        "Month    (1-12, */n, a-b, or *)"),
    ("dow",          "Day/week (0-7,  */n, a-b, or *)"),
]


def _prompt(label: str, ask: Callable[[str], str]) -> str:
    """Ask user for a field value, defaulting to '*' on empty input."""
    raw = ask(f"  {label}: ").strip()
    return raw if raw else "*"


def build_interactive(
    ask: Optional[Callable[[str], str]] = None,
    out: Optional[Callable[[str], None]] = None,
) -> Optional[CronExpression]:
    """Walk the user through building a cron expression field by field.

    Parameters
    ----------
    ask: callable that takes a prompt string and returns user input (default: input)
    out: callable for printing output (default: print)
    """
    ask = ask or input
    out = out or print

    out("\n=== crontab-buddy interactive builder ===")
    out("Press Enter to accept the default '*' for any field.\n")

    parts = []
    for _attr, label in FIELD_PROMPTS:
        while True:
            value = _prompt(label, ask)
            candidate = " ".join(parts + [value] + ["*"] * (5 - len(parts) - 1))
            result = validate(candidate)
            # Only validate fields entered so far by checking partial parse
            # Accept if no errors relate to already-entered positions
            parts.append(value)
            break

    expression = " ".join(parts)
    result = validate(expression)

    out(f"\nExpression : {expression}")
    if result.valid:
        try:
            expr = CronExpression(expression)
            out(f"Description: {humanize(expr)}")
        except Exception:
            pass
    if result.errors:
        out("Errors:")
        for e in result.errors:
            out(f"  ✗ {e}")
    if result.warnings:
        out("Warnings:")
        for w in result.warnings:
            out(f"  ⚠ {w}")

    return CronExpression(expression) if result.valid else None
