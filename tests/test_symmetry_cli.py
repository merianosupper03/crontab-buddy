import json
import pytest
from io import StringIO
from unittest.mock import patch
from crontab_buddy.symmetry_cli import (
    cmd_symmetry_check,
    cmd_symmetry_score,
    cmd_symmetry_label,
    cmd_symmetry_json,
    cmd_symmetry_batch,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def captured(capsys):
    return capsys


def test_cmd_check_prints_expression(captured):
    args = Args(expr_a="0 9 * * 1", expr_b="0 9 * * 1")
    cmd_symmetry_check(args)
    out = captured.readouterr().out
    assert "0 9 * * 1" in out


def test_cmd_check_symmetric_no_differences(captured):
    args = Args(expr_a="0 9 * * 1", expr_b="0 9 * * 1")
    cmd_symmetry_check(args)
    out = captured.readouterr().out
    assert "Symmetric    : True" in out
    assert "No field differences" in out


def test_cmd_check_asymmetric_shows_differences(captured):
    args = Args(expr_a="0 9 * * 1", expr_b="0 10 * * 1")
    cmd_symmetry_check(args)
    out = captured.readouterr().out
    assert "Symmetric    : False" in out
    assert "hour" in out


def test_cmd_score_prints_float(captured):
    args = Args(expr_a="0 9 * * *", expr_b="0 9 * * *")
    cmd_symmetry_score(args)
    out = captured.readouterr().out.strip()
    score = float(out)
    assert 0.0 <= score <= 1.0


def test_cmd_label_prints_string(captured):
    args = Args(expr_a="0 9 * * *", expr_b="30 22 * * *")
    cmd_symmetry_label(args)
    out = captured.readouterr().out.strip()
    assert isinstance(out, str)
    assert len(out) > 0


def test_cmd_json_valid_structure(captured):
    args = Args(expr_a="0 9 * * 1", expr_b="0 10 * * 2")
    cmd_symmetry_json(args)
    out = captured.readouterr().out
    data = json.loads(out)
    assert "expr_a" in data
    assert "expr_b" in data
    assert "symmetric" in data
    assert "score" in data
    assert "label" in data
    assert "differences" in data


def test_cmd_batch_prints_results(captured):
    args = Args(pairs=["0 9 * * *, 0 9 * * *", "0 9 * * *, 0 10 * * *"])
    cmd_symmetry_batch(args)
    out = captured.readouterr().out
    assert "YES" in out or "NO" in out
    assert "score=" in out


def test_cmd_batch_ignores_malformed_lines(captured):
    args = Args(pairs=["notavalidpair", "0 9 * * *, 0 9 * * *"])
    cmd_symmetry_batch(args)
    out = captured.readouterr().out
    lines = [l for l in out.strip().splitlines() if l]
    assert len(lines) == 1
