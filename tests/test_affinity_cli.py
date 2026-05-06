"""Tests for crontab_buddy.affinity_cli."""

import json
from io import StringIO
from unittest.mock import patch

import pytest
from crontab_buddy.affinity_cli import (
    cmd_affinity_check,
    cmd_affinity_score,
    cmd_affinity_grade,
    cmd_affinity_json,
    cmd_affinity_batch,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture()
def captured(capsys):
    yield capsys


def test_cmd_check_prints_grade(captured):
    cmd_affinity_check(Args(expr_a="0 * * * *", expr_b="30 * * * *"))
    out = captured.readouterr().out
    assert "Grade" in out


def test_cmd_score_prints_float(captured):
    cmd_affinity_score(Args(expr_a="0 * * * *", expr_b="30 * * * *"))
    out = captured.readouterr().out.strip()
    score = float(out)
    assert 0.0 <= score <= 1.0


def test_cmd_grade_prints_label(captured):
    cmd_affinity_grade(Args(expr_a="0 6 * * *", expr_b="0 18 * * *"))
    out = captured.readouterr().out.strip()
    assert out in ("Excellent", "Good", "Fair", "Poor")


def test_cmd_json_is_valid_json(captured):
    cmd_affinity_json(Args(expr_a="0 * * * *", expr_b="30 * * * *"))
    out = captured.readouterr().out
    data = json.loads(out)
    assert "score" in data
    assert "grade" in data
    assert "overlap_count" in data


def test_cmd_json_contains_expressions(captured):
    cmd_affinity_json(Args(expr_a="0 * * * *", expr_b="0 12 * * *"))
    out = captured.readouterr().out
    data = json.loads(out)
    assert data["expression_a"] == "0 * * * *"
    assert data["expression_b"] == "0 12 * * *"


def test_cmd_batch_valid_pairs(captured):
    pairs = "0 * * * *|30 * * * *\n0 6 * * *|0 18 * * *"
    cmd_affinity_batch(Args(pairs=pairs))
    out = captured.readouterr().out
    assert "<->" in out


def test_cmd_batch_no_valid_pairs_prints_message(captured):
    cmd_affinity_batch(Args(pairs="no pipes here\nalso no pipes"))
    out = captured.readouterr().out
    assert "No valid pairs" in out
