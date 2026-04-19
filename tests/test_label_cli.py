import pytest
from pathlib import Path
from crontab_buddy.label_cli import (
    cmd_label_add, cmd_label_remove, cmd_label_list, cmd_label_find, cmd_label_all
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


(tmp_path):
    return tmp_path / "labels.json"


def test_cmd_label_add_prints_labeled(tp, capsys):
    cmd_label_add(Args(expression="* * * * *", label="frequent"), path=tp)
    out = capsys.readouterr().out
    assert "frequent" in out
    assert "Labeled" in out


def test_cmd_label_add_duplicate_message(tp, capsys):
    cmd_label_add(Args(expression="* * * * *", label="frequent"), path=tp)
    cmd_label_add(Args(expression="* * * * *", label="frequent"), path=tp)
    out = capsys.readouterr().out
    assert "already has label" in out


def test_cmd_label_remove_success(tp, capsys):
    cmd_label_add(Args(expression="0 * * * *", label="hourly"), path=tp)
    capsys.readouterr()
    cmd_label_remove(Args(expression="0 * * * *", label="hourly"), path=tp)
    out = capsys.readouterr().out
    assert "Removed" in out


def test_cmd_label_remove_missing(tp, capsys):
    cmd_label_remove(Args(expression="0 * * * *", label="ghost"), path=tp)
    out = capsys.readouterr().out
    assert "not found" in out


def test_cmd_label_list_with_labels(tp, capsys):
    cmd_label_add(Args(expression="0 0 * * *", label="daily"), path=tp)
    capsn    cmd_label_list(Args(expression="0 0 * * *"), path=tp)
    out = capsys.readouterr().out
    assert "daily" in out


def test_cmd_label_list_empty(tp, capsys):
    cmd_label_list(Args(expression="0 0 * * *"), path=tp)
    out = capsys.readouterr().out
    assert "No labels" in out


def test_cmd_label_find_results(tp, capsys):
    cmd_label_add(Args(expression="* * * * *", label="tag1"), path=tp)
    capsys.readouterr()
    cmd_label_find(Args(label="tag1"), path=tp)
    out = capsys.readouterr().out
    assert "* * * * *" in out


def test_cmd_label_all_empty(tp, capsys):
    cmd_label_all(Args(), path=tp)
    out = capsys.readouterr().out
    assert "No labels" in out
