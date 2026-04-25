"""Tests for crontab_buddy.healthcheck and healthcheck_cli."""
import pytest

from crontab_buddy.healthcheck import (
    delete_healthcheck,
    get_healthcheck,
    list_healthchecks,
    set_healthcheck,
)
from crontab_buddy.healthcheck_cli import (
    cmd_healthcheck_delete,
    cmd_healthcheck_get,
    cmd_healthcheck_list,
    cmd_healthcheck_set,
)


@pytest.fixture()
def tmp_hc(tmp_path):
    return str(tmp_path / "hc.json")


def test_set_and_get(tmp_hc):
    set_healthcheck("0 * * * *", "https://hc.example.com/ping/abc", path=tmp_hc)
    hc = get_healthcheck("0 * * * *", path=tmp_hc)
    assert hc is not None
    assert hc["url"] == "https://hc.example.com/ping/abc"
    assert hc["method"] == "ping"
    assert hc["grace_seconds"] == 60


def test_get_missing_returns_none(tmp_hc):
    assert get_healthcheck("*/5 * * * *", path=tmp_hc) is None


def test_overwrite_healthcheck(tmp_hc):
    set_healthcheck("0 * * * *", "https://old.example.com", path=tmp_hc)
    set_healthcheck("0 * * * *", "https://new.example.com", grace_seconds=120, path=tmp_hc)
    hc = get_healthcheck("0 * * * *", path=tmp_hc)
    assert hc["url"] == "https://new.example.com"
    assert hc["grace_seconds"] == 120


def test_delete_existing(tmp_hc):
    set_healthcheck("0 * * * *", "https://hc.example.com/ping", path=tmp_hc)
    assert delete_healthcheck("0 * * * *", path=tmp_hc) is True
    assert get_healthcheck("0 * * * *", path=tmp_hc) is None


def test_delete_missing_returns_false(tmp_hc):
    assert delete_healthcheck("0 * * * *", path=tmp_hc) is False


def test_invalid_method_raises(tmp_hc):
    with pytest.raises(ValueError, match="method"):
        set_healthcheck("0 * * * *", "https://hc.example.com", method="webhook", path=tmp_hc)


def test_invalid_url_raises(tmp_hc):
    with pytest.raises(ValueError, match="url"):
        set_healthcheck("0 * * * *", "ftp://bad.example.com", path=tmp_hc)


def test_negative_grace_raises(tmp_hc):
    with pytest.raises(ValueError, match="grace_seconds"):
        set_healthcheck("0 * * * *", "https://hc.example.com", grace_seconds=-1, path=tmp_hc)


def test_list_healthchecks(tmp_hc):
    set_healthcheck("0 * * * *", "https://hc.example.com/a", path=tmp_hc)
    set_healthcheck("*/5 * * * *", "https://hc.example.com/b", path=tmp_hc)
    items = list_healthchecks(path=tmp_hc)
    assert len(items) == 2
    exprs = {i["expression"] for i in items}
    assert "0 * * * *" in exprs
    assert "*/5 * * * *" in exprs


class Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


@pytest.fixture()
def tp(tmp_hc, capsys):
    return tmp_hc, capsys


def test_cmd_set_prints(tp):
    path, capsys = tp
    args = Args(expression="0 * * * *", url="https://hc.example.com/ping", method="ping", grace=30)
    cmd_healthcheck_set(args, path=path)
    out = capsys.readouterr().out
    assert "Health check set" in out
    assert "https://hc.example.com/ping" in out


def test_cmd_set_invalid_url_prints_error(tp):
    path, capsys = tp
    args = Args(expression="0 * * * *", url="not-a-url", method="ping", grace=60)
    cmd_healthcheck_set(args, path=path)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_get_existing(tp):
    path, capsys = tp
    set_healthcheck("0 * * * *", "https://hc.example.com/ping", path=path)
    args = Args(expression="0 * * * *")
    cmd_healthcheck_get(args, path=path)
    out = capsys.readouterr().out
    assert "https://hc.example.com/ping" in out


def test_cmd_get_missing(tp):
    path, capsys = tp
    args = Args(expression="0 * * * *")
    cmd_healthcheck_get(args, path=path)
    out = capsys.readouterr().out
    assert "No health check" in out


def test_cmd_list_empty(tp):
    path, capsys = tp
    cmd_healthcheck_list(Args(), path=path)
    out = capsys.readouterr().out
    assert "No health checks" in out


def test_cmd_delete_success(tp):
    path, capsys = tp
    set_healthcheck("0 * * * *", "https://hc.example.com/ping", path=path)
    args = Args(expression="0 * * * *")
    cmd_healthcheck_delete(args, path=path)
    out = capsys.readouterr().out
    assert "Removed" in out
