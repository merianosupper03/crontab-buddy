import pytest
from crontab_buddy.snapshot import save_snapshot, get_snapshot, delete_snapshot, list_snapshots


@pytest.fixture
def tmp_snap(tmp_path):
    return str(tmp_path / "snapshots.json")


def test_save_and_get(tmp_snap):
    save_snapshot("daily", "0 9 * * *", "morning job", path=tmp_snap)
    snap = get_snapshot("daily", path=tmp_snap)
    assert snap is not None
    assert snap["expression"] == "0 9 * * *"
    assert snap["comment"] == "morning job"
    assert "saved_at" in snap


def test_get_missing_returns_none(tmp_snap):
    assert get_snapshot("nope", path=tmp_snap) is None


def test_overwrite_snapshot(tmp_snap):
    save_snapshot("job", "0 9 * * *", path=tmp_snap)
    save_snapshot("job", "0 10 * * *", path=tmp_snap)
    snap = get_snapshot("job", path=tmp_snap)
    assert snap["expression"] == "0 10 * * *"


def test_delete_existing(tmp_snap):
    save_snapshot("temp", "*/5 * * * *", path=tmp_snap)
    result = delete_snapshot("temp", path=tmp_snap)
    assert result is True
    assert get_snapshot("temp", path=tmp_snap) is None


def test_delete_missing(tmp_snap):
    assert delete_snapshot("ghost", path=tmp_snap) is False


def test_list_snapshots(tmp_snap):
    save_snapshot("a", "0 1 * * *", path=tmp_snap)
    save_snapshot("b", "0 2 * * *", path=tmp_snap)
    snaps = list_snapshots(path=tmp_snap)
    names = [s["name"] for s in snaps]
    assert "a" in names
    assert "b" in names


def test_list_empty(tmp_snap):
    assert list_snapshots(path=tmp_snap) == []


def test_snapshot_cli_save_prints(tmp_snap, capsys):
    from crontab_buddy.snapshot_cli import cmd_snapshot_save
    cmd_snapshot_save("myjob", "0 6 * * 1", path=tmp_snap)
    out = capsys.readouterr().out
    assert "myjob" in out
    assert "0 6 * * 1" in out


def test_snapshot_cli_get_missing(tmp_snap, capsys):
    from crontab_buddy.snapshot_cli import cmd_snapshot_get
    cmd_snapshot_get("missing", path=tmp_snap)
    out = capsys.readouterr().out
    assert "No snapshot" in out


def test_snapshot_cli_list_empty(tmp_snap, capsys):
    from crontab_buddy.snapshot_cli import cmd_snapshot_list
    cmd_snapshot_list(path=tmp_snap)
    out = capsys.readouterr().out
    assert "No snapshots" in out
