import pytest
from pathlib import Path
from crontab_buddy.workflow import (
    create_workflow, add_step, remove_step,
    get_workflow, delete_workflow, list_workflows,
)


@pytest.fixture
def tmp_wf(tmp_path):
    return tmp_path / "workflows.json"


def test_create_workflow(tmp_wf):
    assert create_workflow("nightly", path=tmp_wf) is True
    wf = get_workflow("nightly", path=tmp_wf)
    assert wf is not None
    assert wf["name"] == "nightly"
    assert wf["steps"] == []


def test_create_duplicate_returns_false(tmp_wf):
    create_workflow("nightly", path=tmp_wf)
    assert create_workflow("nightly", path=tmp_wf) is False


def test_create_is_case_insensitive(tmp_wf):
    create_workflow("Nightly", path=tmp_wf)
    assert create_workflow("NIGHTLY", path=tmp_wf) is False


def test_add_step(tmp_wf):
    create_workflow("w1", path=tmp_wf)
    ok = add_step("w1", "0 2 * * *", label="backup", path=tmp_wf)
    assert ok is True
    wf = get_workflow("w1", path=tmp_wf)
    assert len(wf["steps"]) == 1
    assert wf["steps"][0]["expression"] == "0 2 * * *"
    assert wf["steps"][0]["label"] == "backup"


def test_add_step_missing_workflow(tmp_wf):
    assert add_step("ghost", "0 * * * *", path=tmp_wf) is False


def test_add_step_default_label(tmp_wf):
    create_workflow("w2", path=tmp_wf)
    add_step("w2", "5 4 * * *", path=tmp_wf)
    wf = get_workflow("w2", path=tmp_wf)
    assert wf["steps"][0]["label"] == "5 4 * * *"


def test_remove_step(tmp_wf):
    create_workflow("w3", path=tmp_wf)
    add_step("w3", "0 1 * * *", path=tmp_wf)
    add_step("w3", "0 2 * * *", path=tmp_wf)
    ok = remove_step("w3", 0, path=tmp_wf)
    assert ok is True
    wf = get_workflow("w3", path=tmp_wf)
    assert len(wf["steps"]) == 1
    assert wf["steps"][0]["expression"] == "0 2 * * *"


def test_remove_step_out_of_range(tmp_wf):
    create_workflow("w4", path=tmp_wf)
    assert remove_step("w4", 5, path=tmp_wf) is False


def test_delete_workflow(tmp_wf):
    create_workflow("temp", path=tmp_wf)
    assert delete_workflow("temp", path=tmp_wf) is True
    assert get_workflow("temp", path=tmp_wf) is None


def test_delete_missing_workflow(tmp_wf):
    assert delete_workflow("ghost", path=tmp_wf) is False


def test_list_workflows(tmp_wf):
    create_workflow("alpha", path=tmp_wf)
    create_workflow("beta", path=tmp_wf)
    names = [w["name"] for w in list_workflows(path=tmp_wf)]
    assert "alpha" in names
    assert "beta" in names
