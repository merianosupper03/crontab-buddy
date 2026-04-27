"""Tests for crontab_buddy.annotation_cli."""

import pytest
from unittest.mock import patch
from types import SimpleNamespace
from crontab_buddy.annotation_cli import (
    cmd_annotation_add,
    cmd_annotation_get,
    cmd_annotation_delete,
    cmd_annotation_clear,
    cmd_annotation_list,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def tp(tmp_path):
    ann_path = tmp_path / "annotations.json"
    with patch("crontab_buddy.annotation_cli.add_annotation") as mock_add, \
         patch("crontab_buddy.annotation_cli.get_annotations") as mock_get, \
         patch("crontab_buddy.annotation_cli.delete_annotation") as mock_del, \
         patch("crontab_buddy.annotation_cli.clear_annotations") as mock_clr, \
         patch("crontab_buddy.annotation_cli.list_all_annotations") as mock_list:
        yield SimpleNamespace(
            path=ann_path,
            add=mock_add,
            get=mock_get,
            delete=mock_del,
            clear=mock_clr,
            list=mock_list,
        )


def test_cmd_add_prints(tp):
    tp.add.return_value = {"text": "my note", "author": None}
    out = []
    cmd_annotation_add(Args(expression="* * * * *", text="my note"), print_fn=out.append)
    assert any("my note" in line for line in out)


def test_cmd_add_with_author_prints_author(tp):
    tp.add.return_value = {"text": "note", "author": "bob"}
    out = []
    cmd_annotation_add(Args(expression="* * * * *", text="note", author="bob"), print_fn=out.append)
    assert any("bob" in line for line in out)


def test_cmd_add_invalid_text_prints_error(tp):
    tp.add.side_effect = ValueError("Annotation text must not be empty.")
    out = []
    cmd_annotation_add(Args(expression="* * * * *", text=""), print_fn=out.append)
    assert any("Error" in line for line in out)


def test_cmd_get_existing(tp):
    tp.get.return_value = [{"text": "important", "author": None}]
    out = []
    cmd_annotation_get(Args(expression="0 9 * * 1"), print_fn=out.append)
    assert any("important" in line for line in out)


def test_cmd_get_no_annotations(tp):
    tp.get.return_value = []
    out = []
    cmd_annotation_get(Args(expression="0 9 * * 1"), print_fn=out.append)
    assert any("No annotations" in line for line in out)


def test_cmd_delete_success(tp):
    tp.delete.return_value = True
    out = []
    cmd_annotation_delete(Args(expression="* * * * *", index=0), print_fn=out.append)
    assert any("deleted" in line for line in out)


def test_cmd_delete_missing(tp):
    tp.delete.return_value = False
    out = []
    cmd_annotation_delete(Args(expression="* * * * *", index=99), print_fn=out.append)
    assert any("No annotation" in line for line in out)


def test_cmd_clear_prints_count(tp):
    tp.clear.return_value = 3
    out = []
    cmd_annotation_clear(Args(expression="*/5 * * * *"), print_fn=out.append)
    assert any("3" in line for line in out)


def test_cmd_list_empty(tp):
    tp.list.return_value = {}
    out = []
    cmd_annotation_list(Args(), print_fn=out.append)
    assert any("No annotations" in line for line in out)


def test_cmd_list_with_entries(tp):
    tp.list.return_value = {"0 0 * * *": [{"text": "midnight", "author": None}]}
    out = []
    cmd_annotation_list(Args(), print_fn=out.append)
    assert any("0 0 * * *" in line for line in out)
