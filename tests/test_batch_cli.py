import pytest
from unittest.mock import patch, MagicMock
from crontab_buddy import batch_cli


class Args:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_cmd_batch_validate_prints_ok(capsys):
    args = Args(expressions=["0 9 * * 1"])
    batch_cli.cmd_batch_validate(args)
    out = capsys.readouterr().out
    assert "[OK]" in out
    assert "0 9 * * 1" in out


def test_cmd_batch_validate_prints_fail(capsys):
    args = Args(expressions=["99 9 * * 1"])
    batch_cli.cmd_batch_validate(args)
    out = capsys.readouterr().out
    assert "[FAIL]" in out


def test_cmd_batch_validate_summary(capsys):
    args = Args(expressions=["0 9 * * 1", "99 9 * * 1"])
    batch_cli.cmd_batch_validate(args)
    out = capsys.readouterr().out
    assert "Total: 2" in out
    assert "Valid: 1" in out
    assert "Invalid: 1" in out


def test_cmd_batch_file_not_found(capsys):
    args = Args(file="/nonexistent/path.txt")
    batch_cli.cmd_batch_file(args)
    out = capsys.readouterr().out
    assert "not found" in out.lower()


def test_cmd_batch_file_valid(tmp_path, capsys):
    f = tmp_path / "e.txt"
    f.write_text("0 9 * * 1\n")
    args = Args(file=str(f))
    batch_cli.cmd_batch_file(args)
    out = capsys.readouterr().out
    assert "[OK]" in out


def test_cmd_batch_json_output(capsys):
    import json
    args = Args(expressions=["0 9 * * 1"], file=None)
    batch_cli.cmd_batch_json(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "summary" in data
    assert "results" in data
    assert data["summary"]["total"] == 1
