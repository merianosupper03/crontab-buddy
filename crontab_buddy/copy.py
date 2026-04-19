"""Copy/duplicate cron expressions with optional field overrides."""

from typing import Optional, Dict
from crontab_buddy.parser import CronExpression, CronParseError

FIELD_NAMES = ["minute", "hour", "dom", "month", "dow"]


def copy_expression(
    expr: str,
    minute: Optional[str] = None,
    hour: Optional[str] = None,
    dom: Optional[str] = None,
    month: Optional[str] = None,
    dow: Optional[str] = None,
) -> CronExpression:
    """Parse expr and return a new CronExpression with optional field overrides."""
    parsed = CronExpression(expr)
    fields = list(parsed.fields)

    overrides = [minute, hour, dom, month, dow]
    for i, override in enumerate(overrides):
        if override is not None:
            fields[i] = override

    new_expr = " ".join(fields)
    return CronExpression(new_expr)


def copy_with_dict(expr: str, overrides: Dict[str, str]) -> CronExpression:
    """Apply a dict of field overrides {field_name: value} to a copy of expr."""
    unknown = set(overrides) - set(FIELD_NAMES)
    if unknown:
        raise ValueError(f"Unknown field(s): {', '.join(sorted(unknown))}")

    kwargs = {name: overrides.get(name) for name in FIELD_NAMES}
    return copy_expression(expr, **kwargs)


def describe_diff(original: str, copied: str) -> Dict[str, Dict[str, str]]:
    """Return a mapping of changed fields with before/after values."""
    a = CronExpression(original)
    b = CronExpression(copied)
    changes = {}
    for name, va, vb in zip(FIELD_NAMES, a.fields, b.fields):
        if va != vb:
            changes[name] = {"before": va, "after": vb}
    return changes
