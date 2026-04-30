"""Tests for crontab_buddy.observability_cli."""

import pytest
from unittest.mock import patch
from crontab_buddy.observability_cli import (
    cmd_observability_delete,
    cmd_observability_get,
    cmd_observability_list,
    cmd_observability_set,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def tp(tmp_path, capsys):
    return tmp_path / "obs.json", capsys


def test_cmd_set_prints(tp):
    path, capsys = tp
    args = Args(expression="0 * * * *", log_level="info", trace_backend="none",
                metrics_enabled=False, path=str(path))
    cmd_observability_set(args)
    out = capsys.readouterr().out
    assert "0 * * * *" in out


def test_cmd_set_invalid_log_level_prints_error(tp):
    path, capsys = tp
    args = Args(expression="0 * * * *", log_level="loud", trace_backend="none",
                metrics_enabled=False, path=str(path))
    cmd_observability_set(args)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_get_existing(tp):
    path, capsys = tp
    set_args = Args(expression="5 4 * * *", log_level="warning",
                    trace_backend="zipkin", metrics_enabled=True, path=str(path))
    cmd_observability_set(set_args)
    capsys.readouterr()
    get_args = Args(expression="5 4 * * *", path=str(path))
    cmd_observability_get(get_args)
    out = capsys.readouterr().out
    assert "warning" in out
    assert "zipkin" in out
    assert "enabled" in out


def test_cmd_get_missing(tp):
    path, capsys = tp
    args = Args(expression="1 2 3 4 5", path=str(path))
    cmd_observability_get(args)
    out = capsys.readouterr().out
    assert "No observability" in out


def test_cmd_delete_success(tp):
    path, capsys = tp
    set_args = Args(expression="0 0 * * *", log_level="info", trace_backend="none",
                    metrics_enabled=False, path=str(path))
    cmd_observability_set(set_args)
    capsys.readouterr()
    del_args = Args(expression="0 0 * * *", path=str(path))
    cmd_observability_delete(del_args)
    out = capsys.readouterr().out
    assert "Removed" in out


def test_cmd_delete_missing(tp):
    path, capsys = tp
    args = Args(expression="9 9 9 9 *", path=str(path))
    cmd_observability_delete(args)
    out = capsys.readouterr().out
    assert "No config" in out


def test_cmd_list_shows_entries(tp):
    path, capsys = tp
    for expr in ["0 * * * *", "*/10 * * * *"]:
        a = Args(expression=expr, log_level="debug", trace_backend="none",
                 metrics_enabled=False, path=str(path))
        cmd_observability_set(a)
    capsys.readouterr()
    cmd_observability_list(Args(path=str(path)))
    out = capsys.readouterr().out
    assert "0 * * * *" in out
    assert "*/10 * * * *" in out


def test_cmd_list_empty(tp):
    path, capsys = tp
    cmd_observability_list(Args(path=str(path)))
    out = capsys.readouterr().out
    assert "No observability" in out
