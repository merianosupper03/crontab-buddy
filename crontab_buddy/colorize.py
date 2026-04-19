"""Colorized output helpers for cron expressions and descriptions."""

TRY_COLORS = True

try:
    from colorama import Fore, Style, init as _init
    _init(autoreset=True)
except ImportError:
    TRY_COLORS = False


def _c(text: str, color_code: str) -> str:
    if not TRY_COLORS:
        return text
    return f"{color_code}{text}{Style.RESET_ALL}"


FIELD_COLORS = [
    Fore.CYAN if TRY_COLORS else "",
    Fore.GREEN if TRY_COLORS else "",
    Fore.YELLOW if TRY_COLORS else "",
    Fore.MAGENTA if TRY_COLORS else "",
    Fore.BLUE if TRY_COLORS else "",
]

FIELD_NAMES = ["minute", "hour", "day-of-month", "month", "day-of-week"]


def colorize_expression(expression: str) -> str:
    """Return a colorized version of a 5-field cron expression string."""
    fields = expression.split()
    if len(fields) != 5:
        return expression
    colored = []
    for i, field in enumerate(fields):
        color = FIELD_COLORS[i] if TRY_COLORS else ""
        colored.append(_c(field, color))
    return "  ".join(colored)


def colorize_description(description: str) -> str:
    """Wrap description in a subtle style."""
    if not TRY_COLORS:
        return description
    return _c(description, Style.BRIGHT)


def field_legend() -> str:
    """Return a color-coded legend of field names."""
    parts = []
    for i, name in enumerate(FIELD_NAMES):
        color = FIELD_COLORS[i] if TRY_COLORS else ""
        parts.append(_c(name, color))
    return "  ".join(parts)
