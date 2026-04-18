"""Built-in cron expression templates for common scheduling patterns."""

from typing import Optional
from crontab_buddy.parser import CronExpression, CronParseError

_TEMPLATES: dict[str, dict] = {
    "every-minute": {
        "expression": "* * * * *",
        "description": "Run every minute",
        "tags": ["frequent"],
    },
    "every-hour": {
        "expression": "0 * * * *",
        "description": "Run at the start of every hour",
        "tags": ["hourly"],
    },
    "daily-midnight": {
        "expression": "0 0 * * *",
        "description": "Run once a day at midnight",
        "tags": ["daily"],
    },
    "daily-noon": {
        "expression": "0 12 * * *",
        "description": "Run once a day at noon",
        "tags": ["daily"],
    },
    "weekly-sunday": {
        "expression": "0 0 * * 0",
        "description": "Run every Sunday at midnight",
        "tags": ["weekly"],
    },
    "monthly-first": {
        "expression": "0 0 1 * *",
        "description": "Run on the first day of every month",
        "tags": ["monthly"],
    },
    "weekdays-9am": {
        "expression": "0 9 * * 1-5",
        "description": "Run at 9am on weekdays",
        "tags": ["weekday", "business"],
    },
    "every-5-minutes": {
        "expression": "*/5 * * * *",
        "description": "Run every 5 minutes",
        "tags": ["frequent"],
    },
    "every-15-minutes": {
        "expression": "*/15 * * * *",
        "description": "Run every 15 minutes",
        "tags": ["frequent"],
    },
    "twice-daily": {
        "expression": "0 0,12 * * *",
        "description": "Run at midnight and noon",
        "tags": ["daily"],
    },
}


def list_templates() -> list[dict]:
    """Return all templates with their names."""
    return [{"name": k, **v} for k, v in _TEMPLATES.items()]


def get_template(name: str) -> Optional[dict]:
    """Return a single template by name, or None if not found."""
    entry = _TEMPLATES.get(name.lower())
    if entry is None:
        return None
    return {"name": name.lower(), **entry}


def search_templates(keyword: str) -> list[dict]:
    """Search templates by keyword in name, description, or tags."""
    keyword = keyword.lower()
    results = []
    for name, data in _TEMPLATES.items():
        if (
            keyword in name
            or keyword in data["description"].lower()
            or any(keyword in t for t in data["tags"])
        ):
            results.append({"name": name, **data})
    return results


def template_to_expression(name: str) -> Optional[CronExpression]:
    """Parse a template's expression into a CronExpression, or None."""
    tmpl = get_template(name)
    if tmpl is None:
        return None
    try:
        return CronExpression(tmpl["expression"])
    except CronParseError:
        return None
