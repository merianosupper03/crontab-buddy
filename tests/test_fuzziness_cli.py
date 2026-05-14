"""Tests for crontab_buddy.fuzziness_cli."""

import io
import sys
import pytest
from crontab_buddy.fuzziness_cli import (
    cmd_fuzziness_check,
    cmd_fuzziness_score,
    cmd_fuzziness_grade,
    cmd_fuzziness_batch,
    cmd_fuzziness_json,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def captured(fn, args):
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        fn(args)
    finally:
        sys.stdout = old
    return buf.getvalue()


def test_cmd_check_prints_expression():
    out = captured(cmd_fuzziness_check, Args(expression="* * * * *"))
    assert "* * * * *" in out


def test_cmd_check_prints_grade():
    out = captured(cmd_fuzziness_check, Args(expression="* * * * *"))
    assert "nebulous" in out


def test_cmd_check_prints_score():
    out = captured(cmd_fuzziness_check, Args(expression="* * * * *"))
    assert "1.000" in out


def test_cmd_check_invalid_prints_error():
    out = captured(cmd_fuzziness_check, Args(expression="bad cron"))
    assert "error" in out.lower() or "Error" in out


def test_cmd_score_prints_float():
    out = captured(cmd_fuzziness_score, Args(expression="* * * * *"))
    assert float(out.strip()) == pytest.approx(1.0)


def test_cmd_score_invalid_prints_error():
    out = captured(cmd_fuzziness_score, Args(expression="bad"))
    assert "error" in out.lower()


def test_cmd_grade_prints_label():
    out = captured(cmd_fuzziness_grade, Args(expression="0 9 1 1 1"))
    assert out.strip() == "crisp"


def test_cmd_grade_invalid_prints_error():
    out = captured(cmd_fuzziness_grade, Args(expression="bad"))
    assert "error" in out.lower()


def test_cmd_batch_prints_rows():
    out = captured(cmd_fuzziness_batch, Args(expressions=["* * * * *", "0 9 * * *"]))
    lines = [l for l in out.strip().splitlines() if l]
    assert len(lines) == 2


def test_cmd_batch_invalid_shows_error():
    out = captured(cmd_fuzziness_batch, Args(expressions=["bad"]))
    assert "error" in out.lower()


def test_cmd_json_contains_grade():
    import json
    out = captured(cmd_fuzziness_json, Args(expression="* * * * *"))
    data = json.loads(out)
    assert data["grade"] == "nebulous"


def test_cmd_json_contains_scores():
    import json
    out = captured(cmd_fuzziness_json, Args(expression="* * * * *"))
    data = json.loads(out)
    assert "scores" in data
    assert len(data["scores"]) == 5
