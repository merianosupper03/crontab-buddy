"""Tests for crontab_buddy.anomaly and crontab_buddy.anomaly_cli."""

import json
import pytest
from crontab_buddy.anomaly import detect_anomalies, AnomalyResult
from crontab_buddy.anomaly_cli import cmd_anomaly_check, cmd_anomaly_json, cmd_anomaly_batch


# ---------------------------------------------------------------------------
# detect_anomalies
# ---------------------------------------------------------------------------

def test_clean_expression_returns_ok():
    result = detect_anomalies("0 9 * * 1")
    assert result.ok
    assert result.anomalies == []


def test_invalid_expression_returns_error():
    result = detect_anomalies("not a cron")
    assert not result.ok
    assert any("invalid" in a for a in result.anomalies)


def test_dom_and_dow_both_set_flagged():
    result = detect_anomalies("0 9 15 * 1")
    assert not result.ok
    assert any("day-of-month" in a for a in result.anomalies)


def test_february_30_flagged():
    result = detect_anomalies("0 9 30 2 *")
    assert not result.ok
    assert any("February" in a for a in result.anomalies)


def test_redundant_step_one_flagged():
    result = detect_anomalies("*/1 * * * *")
    assert not result.ok
    assert any("redundant" in a.lower() or "step" in a.lower() for a in result.anomalies)


def test_str_ok():
    result = AnomalyResult(expression="0 9 * * *", anomalies=[])
    assert "no anomalies" in str(result)


def test_str_with_anomalies():
    result = AnomalyResult(expression="0 9 15 * 1", anomalies=["some issue"])
    assert "some issue" in str(result)


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def test_cmd_anomaly_check_ok(capsys):
    out = []
    cmd_anomaly_check(Args(expression="0 9 * * 1"), print_fn=out.append)
    assert any("OK" in line for line in out)


def test_cmd_anomaly_check_flags_issue(capsys):
    out = []
    cmd_anomaly_check(Args(expression="0 9 15 * 1"), print_fn=out.append)
    assert any("ANOMALIES" in line for line in out)


def test_cmd_anomaly_json_valid_json():
    out = []
    cmd_anomaly_json(Args(expression="0 9 * * *"), print_fn=out.append)
    payload = json.loads("\n".join(out))
    assert "expression" in payload
    assert "ok" in payload
    assert "anomalies" in payload


def test_cmd_anomaly_batch_summary():
    out = []
    exprs = "0 9 * * *\n0 9 15 * 1"
    cmd_anomaly_batch(Args(expressions=exprs), print_fn=out.append)
    summary = [l for l in out if "/" in l and "expression" in l]
    assert len(summary) == 1
    assert "1/2" in summary[0]
