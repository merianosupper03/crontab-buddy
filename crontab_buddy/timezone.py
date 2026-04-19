"""Timezone-aware next-run display utilities."""

from datetime import datetime
from typing import List, Optional

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError  # Python 3.9+
except ImportError:
    from backports.zoneinfo import ZoneInfo, ZoneInfoNotFoundError  # type: ignore


def convert_runs(runs: List[datetime], tz_name: str) -> List[datetime]:
    """Convert a list of UTC datetimes to the given timezone."""
    try:
        tz = ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, KeyError):
        raise ValueError(f"Unknown timezone: {tz_name!r}")
    return [dt.astimezone(tz) for dt in runs]


def format_runs(runs: List[datetime], tz_name: Optional[str] = None) -> List[str]:
    """Format datetimes as strings, optionally converting to a timezone first."""
    if tz_name:
        runs = convert_runs(runs, tz_name)
        label = tz_name
    else:
        label = "UTC"
    return [f"{dt.strftime('%Y-%m-%d %H:%M:%S')} {label}" for dt in runs]


def local_timezone() -> str:
    """Return the name of the local system timezone, or 'UTC' as fallback."""
    try:
        return datetime.now().astimezone().tzname() or "UTC"
    except Exception:
        return "UTC"


def is_valid_timezone(tz_name: str) -> bool:
    """Return True if the given timezone name is recognised."""
    try:
        ZoneInfo(tz_name)
        return True
    except (ZoneInfoNotFoundError, KeyError, Exception):
        return False
