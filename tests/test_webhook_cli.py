"""Tests for crontab_buddy.webhook_cli."""

import pytest
from crontab_buddy.webhook_cli import (
    cmd_webhook_set,
    cmd_webhook_get,
    cmd_webhook_delete,
    cmd_webhook_list,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def tp(tmp_path):
    return str(tmp_path / "webhooks.json")


def test_cmd_set_prints(tp, capsys):
    args = Args(expression="0 9 * * 1", url="https://example.com/wh")
    cmd_webhook_set(args, path=tp)
    out = capsys.readouterr().out
    assert "Webhook set" in out
    assert "https://example.com/wh" in out


def test_cmd_set_invalid_url_prints_error(tp, capsys):
    args = Args(expression="0 9 * * 1", url="ftp://bad")
    cmd_webhook_set(args, path=tp)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_get_existing(tp, capsys):
    set_args = Args(expression="0 0 * * *", url="https://notify.me")
    cmd_webhook_set(set_args, path=tp)
    get_args = Args(expression="0 0 * * *")
    cmd_webhook_get(get_args, path=tp)
    out = capsys.readouterr().out
    assert "https://notify.me" in out


def test_cmd_get_missing(tp, capsys):
    args = Args(expression="1 2 3 4 5")
    cmd_webhook_get(args, path=tp)
    out = capsys.readouterr().out
    assert "No webhook" in out


def test_cmd_delete_success(tp, capsys):
    set_args = Args(expression="*/10 * * * *", url="https://hook.io")
    cmd_webhook_set(set_args, path=tp)
    del_args = Args(expression="*/10 * * * *")
    cmd_webhook_delete(del_args, path=tp)
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_delete_missing(tp, capsys):
    args = Args(expression="5 5 5 5 5")
    cmd_webhook_delete(args, path=tp)
    out = capsys.readouterr().out
    assert "No webhook found" in out


def test_cmd_list_empty(tp, capsys):
    cmd_webhook_list(Args(), path=tp)
    out = capsys.readouterr().out
    assert "No webhooks" in out


def test_cmd_list_shows_entries(tp, capsys):
    cmd_webhook_set(Args(expression="0 8 * * *", url="https://morning.hook"), path=tp)
    cmd_webhook_set(Args(expression="0 20 * * *", url="https://evening.hook"), path=tp)
    cmd_webhook_list(Args(), path=tp)
    out = capsys.readouterr().out
    assert "morning.hook" in out
    assert "evening.hook" in out
