import pytest
import os
from crontab_buddy.batch import process_expressions, batch_summary, load_expressions_from_file


VALID_EXPR = "0 9 * * 1"
INVALID_EXPR = "99 9 * * 1"
BAD_FIELDS = "* * *"


def test_process_valid_expression():
    results = process_expressions([VALID_EXPR])
    assert len(results) == 1
    assert results[0]["valid"] is True
    assert results[0]["description"] is not None
    assert results[0]["errors"] == []


def test_process_invalid_expression():
    results = process_expressions([INVALID_EXPR])
    assert results[0]["valid"] is False
    assert len(results[0]["errors"]) > 0


def test_process_bad_field_count():
    results = process_expressions([BAD_FIELDS])
    assert results[0]["valid"] is False
    assert results[0]["description"] is None


def test_process_multiple_mixed():
    results = process_expressions([VALID_EXPR, INVALID_EXPR])
    assert len(results) == 2
    assert results[0]["valid"] is True
    assert results[1]["valid"] is False


def test_process_preserves_expression_string():
    results = process_expressions([VALID_EXPR])
    assert results[0]["expression"] == VALID_EXPR


def test_batch_summary_all_valid():
    results = process_expressions([VALID_EXPR, "* * * * *"])
    s = batch_summary(results)
    assert s["total"] == 2
    assert s["valid"] == 2
    assert s["invalid"] == 0


def test_batch_summary_mixed():
    results = process_expressions([VALID_EXPR, INVALID_EXPR])
    s = batch_summary(results)
    assert s["total"] == 2
    assert s["valid"] == 1
    assert s["invalid"] == 1


def test_load_expressions_from_file(tmp_path):
    f = tmp_path / "exprs.txt"
    f.write_text("0 9 * * 1\n# comment\n\n*/5 * * * *\n")
    exprs = load_expressions_from_file(str(f))
    assert exprs == ["0 9 * * 1", "*/5 * * * *"]


def test_load_expressions_skips_blanks_and_comments(tmp_path):
    f = tmp_path / "exprs.txt"
    f.write_text("# only comments\n\n   \n")
    exprs = load_expressions_from_file(str(f))
    assert exprs == []
