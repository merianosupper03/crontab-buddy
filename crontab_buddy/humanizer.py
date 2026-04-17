"""Convert a parsed CronExpression into a human-readable description."""

from crontab_buddy.parser import CronExpression

MONTH_NAMES = ["", "January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

DOW_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _describe_field(value: str, unit: str, names: list = value == "*":
        return f"every {unit}"
    if value.start"):
        step = value[2:]
        unit}s"
    if "," in value:
        parts = value.split(",")
        labels = [names[int(p)] if names else p for p in parts]
        return ", ".join(labels)
    if "-" in value and "/" not in value:
        start, end = value.split("-")
        if names:
            return f"{names[int(start)]} through {names[int(end)]}"
        return f"{unit} {start} through {end}"
    if "/" in value:
        base, step = value.split("/")
        base_desc = f"from {base}" if base != "*" else ""
        return f"every {step} {unit}s {base_desc}".strip()
    label = names[int(value)] if names else value
    return f"{unit} {label}" if not names else label


def humanize(expr: CronExpression) -> str:
    """Return a plain-English description of a cron expression."""
    minute = _describe_field(expr.minute, "minute")
    hour = _describe_field(expr.hour, "hour")
    dom = _describe_field(expr.day_of_month, "day")
    month = _describe_field(expr.month, "month", MONTH_NAMES)
    dow = _describe_field(expr.day_of_week, "weekday", DOW_NAMES)

    time_part = f"At {minute} past {hour}" if expr.hour != "*" else f"At {minute}"
    if expr.minute == "0" and expr.hour != "*":
        time_part = f"At the start of {hour}"
    if expr.minute == "*" and expr.hour == "*":
        time_part = "Every minute"

    date_parts = []
    if expr.day_of_month != "*":
        date_parts.append(f"on {dom}")
    if expr.month != "*":
        date_parts.append(f"in {month}")
    if expr.day_of_week != "*":
        date_parts.append(f"on {dow}")

    result = time_part
    if date_parts:
        result += ", " + ", ".join(date_parts)
    return result
