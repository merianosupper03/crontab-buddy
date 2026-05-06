"""Tests for crontab_buddy.resilience_cli."""

import pytest
from crontab_buddy.resilience_cli import cmd_resilience_score, cmd_resilience_score_json
import json


class Args:
    def __init__(self, expression, **kwargs):
        self.expression = expression
        for k, v in kwargs.items():
            setattr(self, k, v)


@pytest.fixture
def captured():
    lines = []
    return lines, lines.append


def test_cmd_score_prints_expression(captured):
    out, fn = captured
    cmd_resilience_score(Args("0 * * * *"), print_fn=fn)
    combined = "\n".join(out)
    assert "0 * * * *" in combined


def test_cmd_score_prints_grade(captured):
    out, fn = captured
    cmd_resilience_score(Args("0 * * * *"), print_fn=fn)
    combined = "\n".join(out)
    assert "Grade" in combined


def test_cmd_score_with_retry_flag(captured):
    out, fn = captured
    cmd_resilience_score(Args("0 * * * *", retry=True), print_fn=fn)
    combined = "\n".join(out)
    assert "retry" in combined.lower()


def test_cmd_score_suggestions_shown_when_missing(captured):
    out, fn = captured
    cmd_resilience_score(Args("0 * * * *"), print_fn=fn)
    combined = "\n".join(out)
    assert "Suggestions" in combined


def test_cmd_score_json_is_valid_json(captured):
    out, fn = captured
    cmd_resilience_score_json(Args("0 * * * *"), print_fn=fn)
    data = json.loads("\n".join(out))
    assert "score" in data
    assert "grade" in data
    assert "factors" in data
    assert "suggestions" in data


def test_cmd_score_json_expression_field(captured):
    out, fn = captured
    cmd_resilience_score_json(Args("30 6 * * 1"), print_fn=fn)
    data = json.loads("\n".join(out))
    assert data["expression"] == "30 6 * * 1"


def test_cmd_score_json_all_flags_score_100(captured):
    out, fn = captured
    cmd_resilience_score_json(
        Args("0 * * * *", retry=True, healthcheck=True, timeout=True, lock=True, notify=True),
        print_fn=fn,
    )
    data = json.loads("\n".join(out))
    assert data["score"] == 100
    assert data["grade"] == "A"
