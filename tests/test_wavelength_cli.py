"""Tests for crontab_buddy.wavelength_cli."""
import io
import sys
import pytest
from crontab_buddy.wavelength_cli import (
    cmd_wavelength_check,
    cmd_wavelength_score,
    cmd_wavelength_label,
    cmd_wavelength_batch,
    cmd_wavelength_json,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class captured:
    def __init__(self):
        self._buf = io.StringIO()

    def __enter__(self):
        sys.stdout = self._buf
        return self

    def __exit__(self, *_):
        sys.stdout = sys.__stdout__

    @property
    def text(self):
        return self._buf.getvalue()


def test_cmd_check_prints_expression():
    args = Args(expression="* * * * *")
    with captured() as cap:
        cmd_wavelength_check(args)
    assert "* * * * *" in cap.text


def test_cmd_check_prints_label():
    args = Args(expression="* * * * *")
    with captured() as cap:
        cmd_wavelength_check(args)
    assert "Label" in cap.text


def test_cmd_check_invalid_prints_error():
    args = Args(expression="bad expr")
    with captured() as cap:
        cmd_wavelength_check(args)
    assert "Error" in cap.text


def test_cmd_score_prints_float():
    args = Args(expression="0 * * * *")
    with captured() as cap:
        cmd_wavelength_score(args)
    val = float(cap.text.strip())
    assert 0.0 <= val <= 1.0


def test_cmd_score_invalid_prints_error():
    args = Args(expression="nope")
    with captured() as cap:
        cmd_wavelength_score(args)
    assert "Error" in cap.text


def test_cmd_label_prints_string():
    args = Args(expression="0 0 * * *")
    with captured() as cap:
        cmd_wavelength_label(args)
    assert cap.text.strip() != ""


def test_cmd_batch_prints_multiple():
    args = Args(expressions=["* * * * *", "0 * * * *"])
    with captured() as cap:
        cmd_wavelength_batch(args)
    lines = [l for l in cap.text.splitlines() if l.strip()]
    assert len(lines) == 2


def test_cmd_json_contains_keys():
    args = Args(expression="0 0 * * *")
    import json
    with captured() as cap:
        cmd_wavelength_json(args)
    data = json.loads(cap.text)
    assert "expression" in data
    assert "period_seconds" in data
    assert "score" in data
    assert "label" in data
