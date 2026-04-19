import pytest
from types import SimpleNamespace
from crontab_buddy.pin_cli import (
    cmd_pin_add, cmd_pin_remove, cmd_pin_list, cmd_pin_check, cmd_pin_clear
)
from crontab_buddy.pin import pin_expression


@pytest.fixture
def tp(tmp_path):
    return tmp_path / "pins.json"


def args(expression):
    return SimpleNamespace(expression=expression)


def test_cmd_pin_add_prints_pinned(tp, capsys):
    cmd_pin_add(args("0 * * * *"), path=tp)
    out = capsys.readouterr().out
    assert "Pinned" in out
    assert "0 * * * *" in out


def test_cmd_pin_add_duplicate_message(tp, capsys):
    pin_expression("0 * * * *", path=tp)
    cmd_pin_add(args("0 * * * *"), path=tp)
    out = capsys.readouterr().out
    assert "Already pinned" in out


def test_cmd_pin_remove_success(tp, capsys):
    pin_expression("0 0 * * *", path=tp)
    cmd_pin_remove(args("0 0 * * *"), path=tp)
    out = capsys.readouterr().out
    assert "Unpinned" in out


def test_cmd_pin_remove_missing(tp, capsys):
    cmd_pin_remove(args("0 0 * * *"), path=tp)
    out = capsys.readouterr().out
    assert "Not found" in out


def test_cmd_pin_list_empty(tp, capsys):
    cmd_pin_list(SimpleNamespace(), path=tp)
    out = capsys.readouterr().out
    assert "No pinned" in out


def test_cmd_pin_list_shows_expressions(tp, capsys):
    pin_expression("0 * * * *", path=tp)
    cmd_pin_list(SimpleNamespace(), path=tp)
    out = capsys.readouterr().out
    assert "0 * * * *" in out


def test_cmd_pin_check_pinned(tp, capsys):
    pin_expression("*/10 * * * *", path=tp)
    cmd_pin_check(args("*/10 * * * *"), path=tp)
    out = capsys.readouterr().out
    assert "Pinned" in out


def test_cmd_pin_check_not_pinned(tp, capsys):
    cmd_pin_check(args("*/10 * * * *"), path=tp)
    out = capsys.readouterr().out
    assert "Not pinned" in out


def test_cmd_pin_clear(tp, capsys):
    pin_expression("0 * * * *", path=tp)
    cmd_pin_clear(SimpleNamespace(), path=tp)
    out = capsys.readouterr().out
    assert "cleared" in out
