"""Tests for coverage_density module and CLI."""
import json
import pytest
from io import StringIO
from unittest.mock import patch
from crontab_buddy.coverage_density import (
    assess_coverage_density,
    format_coverage_density,
    CoverageDensityResult,
)
from crontab_buddy.coverage_density_cli import (
    cmd_coverage_density_check,
    cmd_coverage_density_score,
    cmd_coverage_density_grade,
    cmd_coverage_density_json,
)


class Args:
    def __init__(self, expressions):
        self.expressions = expressions


def test_returns_coverage_density_result():
    result = assess_coverage_density(["* * * * *"])
    assert isinstance(result, CoverageDensityResult)


def test_empty_list_has_error():
    result = assess_coverage_density([])
    assert result.error != ""
    assert result.combined_score == 0.0


def test_invalid_expression_has_error():
    result = assess_coverage_density(["not a cron"])
    assert result.error != ""


def test_every_minute_has_high_coverage():
    result = assess_coverage_density(["* * * * *"])
    assert result.coverage_score >= 0.9


def test_every_minute_has_high_density():
    result = assess_coverage_density(["* * * * *"])
    assert result.density_score >= 0.9


def test_every_minute_grade_is_rich():
    result = assess_coverage_density(["* * * * *"])
    assert result.grade == "rich"


def test_combined_score_between_zero_and_one():
    result = assess_coverage_density(["0 9 * * 1"])
    assert 0.0 <= result.combined_score <= 1.0


def test_multiple_expressions_union():
    result = assess_coverage_density(["0 8 * * *", "0 20 * * *"])
    assert result.coverage_score > 0.0


def test_format_returns_dict():
    result = assess_coverage_density(["* * * * *"])
    d = format_coverage_density(result)
    assert isinstance(d, dict)
    for key in ("coverage_score", "density_score", "combined_score", "grade", "error"):
        assert key in d


def test_cmd_check_prints_grade(capsys):
    cmd_coverage_density_check(Args(["* * * * *"]))
    out = capsys.readouterr().out
    assert "Grade" in out


def test_cmd_score_prints_float(capsys):
    cmd_coverage_density_score(Args(["0 0 * * *"]))
    out = capsys.readouterr().out.strip()
    assert float(out) >= 0.0


def test_cmd_grade_prints_string(capsys):
    cmd_coverage_density_grade(Args(["* * * * *"]))
    out = capsys.readouterr().out.strip()
    assert out in ("rich", "balanced", "moderate", "thin", "sparse")


def test_cmd_json_is_valid_json(capsys):
    cmd_coverage_density_json(Args(["* * * * *"]))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "combined_score" in data


def test_cmd_check_prints_error_on_invalid(capsys):
    cmd_coverage_density_check(Args(["bad expr"]))
    out = capsys.readouterr().out
    assert "Error" in out
