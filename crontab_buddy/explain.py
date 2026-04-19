"""Field-by-field explanation of a cron expression."""

from crontab_buddy.parser import CronExpression, CronParseError

FIELD_NAMES = ["minute", "hour", "day-of-month", "month", "day-of-week"]
FIELD_RANGES = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]
DOW_NAMES = {
    "0": "Sunday", "1": "Monday", "2": "Tuesday", "3": "Wednesday",
    "4": "Thursday", "5": "Friday", "6": "Saturday", "7": "Sunday",
}
MONTH_NAMES = {
    "1": "January", "2": "February", "3": "March", "4": "April",
    "5": "May", "6": "June", "7": "July", "8": "August",
    "9": "September", "10": "October", "11": "November", "12": "December",
}


def _explain_field(value: str, index: int) -> str:
    lo, hi = FIELD_RANGES[index]
    name = FIELD_NAMES[index]

    if value == "*":
        return f"{name}: every value ({lo}-{hi})"

    if value.startswith("*/"):
        step = value[2:]
        return f"{name}: every {step} (step), range {lo}-{hi}"

    if "-" in value and "/" in value:
        rng, step = value.split("/")
        return f"{name}: every {step} within {rng}"

    if "-" in value:
        a, b = value.split("-", 1)
        if index == 4:
            a = DOW_NAMES.get(a, a)
            b = DOW_NAMES.get(b, b)
        elif index == 3:
            a = MONTH_NAMES.get(a, a)
            b = MONTH_NAMES.get(b, b)
        return f"{name}: from {a} to {b}"

    if "," in value:
        parts = value.split(",")
        if index == 4:
            parts = [DOW_NAMES.get(p, p) for p in parts]
        elif index == 3:
            parts = [MONTH_NAMES.get(p, p) for p in parts]
        return f"{name}: {', '.join(parts)}"

    label = value
    if index == 4:
        label = DOW_NAMES.get(value, value)
    elif index == 3:
        label = MONTH_NAMES.get(value, value)
    return f"{name}: exactly {label}"


def explain(expression: str) -> list[dict]:
    """Return a list of per-field explanation dicts."""
    try:
        expr = CronExpression(expression)
    except CronParseError as e:
        return [{"error": str(e)}]

    fields = [expr.minute, expr.hour, expr.dom, expr.month, expr.dow]
    return [
        {"field": FIELD_NAMES[i], "raw": fields[i], "description": _explain_field(fields[i], i)}
        for i in range(5)
    ]
