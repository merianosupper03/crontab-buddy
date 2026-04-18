"""Export cron expressions with documentation to various formats."""

from datetime import datetime
from typing import List

from .parser import CronExpression
from .humanizer import humanize
from .scheduler import next_runs


def to_crontab_line(expr: CronExpression, comment: str = "") -> str:
    """Format a single crontab line with optional inline comment."""
    line = str(expr)
    if comment:
        line = f"{line}  # {comment}"
    return line


def to_markdown(expr: CronExpression, command: str = "", now: datetime = None) -> str:
    """Render a cron expression as a Markdown snippet with human description and next runs."""
    if now is None:
        now = datetime.now()

    lines: List[str] = []
    lines.append(f"## Cron Expression: `{expr}`")
    lines.append("")
    lines.append(f"**Schedule:** {humanize(expr)}")
    lines.append("")

    if command:
        lines.append(f"**Command:** `{command}`")
        lines.append("")

    runs = next_runs(expr, now=now, count=5)
    if runs:
        lines.append("**Next 5 runs:**")
        for run in runs:
            lines.append(f"- {run.strftime('%Y-%m-%d %H:%M')}")
    else:
        lines.append("_No upcoming runs found._")

    return "\n".join(lines)


def to_json_dict(expr: CronExpression, command: str = "", now: datetime = None) -> dict:
    """Serialize a cron expression to a plain dict suitable for JSON export."""
    if now is None:
        now = datetime.now()

    runs = next_runs(expr, now=now, count=5)
    return {
        "expression": str(expr),
        "description": humanize(expr),
        "command": command,
        "next_runs": [r.strftime("%Y-%m-%d %H:%M") for r in runs],
    }
