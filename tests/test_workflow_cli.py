import pytest
from crontab_buddy.workflow import create_workflow, add_step
from crontab_buddy.workflow_cli import (
    cmd_workflow_create, cmd_workflow_add, cmd_workflow_remove,
    cmd_workflow_get, cmd_workflow_delete, cmd_workflow_list,
)


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def tp(tmp_path):
    return tmp_path / "workflows.json"


def test_cmd_create_prints(tp, capsys):
    cmd_workflow_create(Args(name="daily"), path=tp)
    assert "created" in capsys.readouterr().out


def test_cmd_create_duplicate_message(tp, capsys):
    cmd_workflow_create(Args(name="daily"), path=tp)
    cmd_workflow_create(Args(name="daily"), path=tp)
    assert "already exists" in capsys.readouterr().out


def test_cmd_add_prints_added(tp, capsys):
    create_workflow("w1", path=tp)
    cmd_workflow_add(Args(name="w1", expression="0 3 * * *", label="cleanup"), path=tp)
    assert "added" in capsys.readouterr().out


def test_cmd_add_missing_workflow(tp, capsys):
    cmd_workflow_add(Args(name="ghost", expression="0 3 * * *", label=None), path=tp)
    assert "not found" in capsys.readouterr().out


def test_cmd_remove_success(tp, capsys):
    create_workflow("w2", path=tp)
    add_step("w2", "0 1 * * *", path=tp)
    cmd_workflow_remove(Args(name="w2", index=0), path=tp)
    assert "removed" in capsys.readouterr().out


def test_cmd_remove_fail(tp, capsys):
    create_workflow("w3", path=tp)
    cmd_workflow_remove(Args(name="w3", index=99), path=tp)
    assert "Could not" in capsys.readouterr().out


def test_cmd_get_existing(tp, capsys):
    create_workflow("w4", path=tp)
    add_step("w4", "*/5 * * * *", label="ping", path=tp)
    cmd_workflow_get(Args(name="w4"), path=tp)
    out = capsys.readouterr().out
    assert "w4" in out
    assert "ping" in out


def test_cmd_get_missing(tp, capsys):
    cmd_workflow_get(Args(name="ghost"), path=tp)
    assert "not found" in capsys.readouterr().out


def test_cmd_delete_success(tp, capsys):
    create_workflow("bye", path=tp)
    cmd_workflow_delete(Args(name="bye"), path=tp)
    assert "deleted" in capsys.readouterr().out


def test_cmd_list_empty(tp, capsys):
    cmd_workflow_list(Args(), path=tp)
    assert "No workflows" in capsys.readouterr().out


def test_cmd_list_shows_names(tp, capsys):
    create_workflow("alpha", path=tp)
    create_workflow("beta", path=tp)
    cmd_workflow_list(Args(), path=tp)
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" in out
