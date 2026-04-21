"""Tests for crontab_buddy.cooldown and cooldown_cli."""

import pytest
from pathlib import Path
from crontab_buddy.cooldown import (
    set_cooldown,
    get_cooldown,
    delete_cooldown,
    list_cooldowns,
)
from crontab_buddy.cooldown_cli import (
    cmd_cooldown_set,
    cmd_cooldown_get,
    cmd_cooldown_delete,
    cmd_cooldown_list,
)


@pytest.fixture
def tmp_cooldown(tmp_path):
    return tmp_path / "cooldowns.json"


def test_set_and_get(tmp_cooldown):
    set_cooldown("0 * * * *", 5, "minutes", path=tmp_cooldown)
    result = get_cooldown("0 * * * *", path=tmp_cooldown)
    assert result == {"amount": 5, "unit": "minutes"}


def test_get_missing_returns_none(tmp_cooldown):
    assert get_cooldown("* * * * *", path=tmp_cooldown) is None


def test_overwrite_cooldown(tmp_cooldown):
    set_cooldown("0 * * * *", 10, "minutes", path=tmp_cooldown)
    set_cooldown("0 * * * *", 2, "hours", path=tmp_cooldown)
    result = get_cooldown("0 * * * *", path=tmp_cooldown)
    assert result == {"amount": 2, "unit": "hours"}


def test_delete_existing(tmp_cooldown):
    set_cooldown("0 * * * *", 1, "days", path=tmp_cooldown)
    assert delete_cooldown("0 * * * *", path=tmp_cooldown) is True
    assert get_cooldown("0 * * * *", path=tmp_cooldown) is None


def test_delete_missing_returns_false(tmp_cooldown):
    assert delete_cooldown("* * * * *", path=tmp_cooldown) is False


def test_list_cooldowns(tmp_cooldown):
    set_cooldown("0 * * * *", 5, "minutes", path=tmp_cooldown)
    set_cooldown("0 0 * * *", 1, "days", path=tmp_cooldown)
    result = list_cooldowns(path=tmp_cooldown)
    assert "0 * * * *" in result
    assert "0 0 * * *" in result


def test_invalid_amount_raises(tmp_cooldown):
    with pytest.raises(ValueError, match="positive"):
        set_cooldown("* * * * *", 0, "minutes", path=tmp_cooldown)


def test_invalid_unit_raises(tmp_cooldown):
    with pytest.raises(ValueError, match="Invalid unit"):
        set_cooldown("* * * * *", 5, "fortnights", path=tmp_cooldown)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def tp(tmp_path):
    return tmp_path / "cooldowns.json"


def test_cmd_set_prints(tmp_path, capsys):
    args = Args(expression="0 * * * *", amount=30, unit="minutes")
    cmd_cooldown_set(args, path=tp(tmp_path))
    out = capsys.readouterr().out
    assert "Cooldown set" in out
    assert "30 minutes" in out


def test_cmd_set_invalid_unit_prints_error(tmp_path, capsys):
    args = Args(expression="0 * * * *", amount=5, unit="eons")
    cmd_cooldown_set(args, path=tp(tmp_path))
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_get_existing(tmp_path, capsys):
    p = tp(tmp_path)
    set_cooldown("0 * * * *", 2, "hours", path=p)
    args = Args(expression="0 * * * *")
    cmd_cooldown_get(args, path=p)
    out = capsys.readouterr().out
    assert "2 hours" in out


def test_cmd_get_missing(tmp_path, capsys):
    args = Args(expression="* * * * *")
    cmd_cooldown_get(args, path=tp(tmp_path))
    out = capsys.readouterr().out
    assert "No cooldown" in out


def test_cmd_list_empty(tmp_path, capsys):
    cmd_cooldown_list(Args(), path=tp(tmp_path))
    out = capsys.readouterr().out
    assert "No cooldowns" in out


def test_cmd_list_shows_entries(tmp_path, capsys):
    p = tp(tmp_path)
    set_cooldown("0 * * * *", 15, "seconds", path=p)
    cmd_cooldown_list(Args(), path=p)
    out = capsys.readouterr().out
    assert "0 * * * *" in out
    assert "15 seconds" in out
