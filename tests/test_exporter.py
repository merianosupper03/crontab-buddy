"""Tests for crontab_buddy.exporter."""

from datetime import datetime

import pytest

from crontab_buddy.parser import CronExpression
from crontab_buddy.exporter import to_crontab_line, to_markdown, to_json_dict

FIXED_NOW = datetime(2024, 1, 15, 12, 0, 0)


def _expr(s: str) -> CronExpression:
    return CronExpression(s)


def test_to_crontab_line_no_comment():
    line = to_crontab_line(_expr("0 9 * * 1"))
    assert line == "0 9 * * 1"


def test_to_crontab_line_with_comment():
    line = to_crontab_line(_expr("0 9 * * 1"), comment="every monday morning")
    assert line == "0 9 * * 1  # every monday morning"


def test_to_markdown_contains_expression():
    md = to_markdown(_expr("*/15 * * * *"), now=FIXED_NOW)
    assert "*/15 * * * *" in md


def test_to_markdown_contains_description():
    md = to_markdown(_expr("0 0 * * *"), now=FIXED_NOW)
    assert "midnight" in md.lower() or "00:00" in md.lower() or "every" in md.lower()


def test_to_markdown_contains_command():
    md = to_markdown(_expr("0 6 * * *"), command="/usr/bin/backup.sh", now=FIXED_NOW)
    assert "/usr/bin/backup.sh" in md


def test_to_markdown_contains_next_runs():
    md = to_markdown(_expr("0 8 * * *"), now=FIXED_NOW)
    assert "2024" in md


def test_to_json_dict_keys():
    result = to_json_dict(_expr("30 4 * * *"), command="echo hi", now=FIXED_NOW)
    assert set(result.keys()) == {"expression", "description", "command", "next_runs"}


def test_to_json_dict_expression():
    result = to_json_dict(_expr("5 4 * * 0"), now=FIXED_NOW)
    assert result["expression"] == "5 4 * * 0"


def test_to_json_dict_next_runs_count():
    result = to_json_dict(_expr("0 * * * *"), now=FIXED_NOW)
    assert len(result["next_runs"]) == 5


def test_to_json_dict_next_runs_format():
    result = to_json_dict(_expr("0 12 * * *"), now=FIXED_NOW)
    for entry in result["next_runs"]:
        datetime.strptime(entry, "%Y-%m-%d %H:%M")  # should not raise
