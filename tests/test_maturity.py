"""Tests for crontab_buddy.maturity."""

import pytest
from unittest.mock import patch

from crontab_buddy.maturity import score_maturity, format_maturity, _grade

EXPR = "0 9 * * 1"


def _all_false():
    """Patch context that makes every check return a falsy value."""
    return {
        "crontab_buddy.maturity.tags.get_tags": [],
        "crontab_buddy.maturity.notes.get_note": None,
        "crontab_buddy.maturity.favorites.get_favorite": None,
        "crontab_buddy.maturity.ownership.get_owner": None,
        "crontab_buddy.maturity.priority.get_priority": None,
        "crontab_buddy.maturity.retry.get_retry": None,
        "crontab_buddy.maturity.timeout.get_timeout": None,
        "crontab_buddy.maturity.healthcheck.get_healthcheck": None,
        "crontab_buddy.maturity.alert.get_alert": None,
        "crontab_buddy.maturity.notify.get_notify": None,
        "crontab_buddy.maturity.metadata.get_all_metadata": {},
        "crontab_buddy.maturity.lock.get_lock": None,
    }


def _patch_all(overrides=None):
    """Return a list of patch objects."""
    targets = _all_false()
    if overrides:
        targets.update(overrides)
    patches = [patch(k, return_value=v) for k, v in targets.items()]
    return patches


def _apply(patches):
    for p in patches:
        p.start()


def _stop(patches):
    for p in patches:
        p.stop()


def test_score_zero_when_nothing_configured():
    ps = _patch_all()
    _apply(ps)
    try:
        result = score_maturity(EXPR)
        assert result["score"] == 0
        assert result["grade"] == "F"
    finally:
        _stop(ps)


def test_score_increases_with_checks():
    ps = _patch_all({
        "crontab_buddy.maturity.tags.get_tags": ["prod"],
        "crontab_buddy.maturity.notes.get_note": "some note",
        "crontab_buddy.maturity.ownership.get_owner": {"owner": "alice"},
    })
    _apply(ps)
    try:
        result = score_maturity(EXPR)
        assert result["score"] > 0
        assert result["checks"]["has tags"] is True
        assert result["checks"]["has note"] is True
        assert result["checks"]["has owner"] is True
    finally:
        _stop(ps)


def test_all_checks_pass_gives_100():
    overrides = {
        "crontab_buddy.maturity.tags.get_tags": ["x"],
        "crontab_buddy.maturity.notes.get_note": "note",
        "crontab_buddy.maturity.favorites.get_favorite": {"name": "fav"},
        "crontab_buddy.maturity.ownership.get_owner": {"owner": "bob"},
        "crontab_buddy.maturity.priority.get_priority": {"level": "high"},
        "crontab_buddy.maturity.retry.get_retry": {"max_attempts": 3},
        "crontab_buddy.maturity.timeout.get_timeout": {"seconds": 60},
        "crontab_buddy.maturity.healthcheck.get_healthcheck": {"url": "http://x"},
        "crontab_buddy.maturity.alert.get_alert": {"channel": "email"},
        "crontab_buddy.maturity.notify.get_notify": {"email": "a@b.com"},
        "crontab_buddy.maturity.metadata.get_all_metadata": {"env": "prod"},
        "crontab_buddy.maturity.lock.get_lock": {"reason": "stable"},
    }
    ps = _patch_all(overrides)
    _apply(ps)
    try:
        result = score_maturity(EXPR)
        assert result["score"] == 100
        assert result["grade"] == "A"
        assert result["missing"] == []
    finally:
        _stop(ps)


def test_missing_list_contains_unconfigured():
    ps = _patch_all()
    _apply(ps)
    try:
        result = score_maturity(EXPR)
        assert "has owner" in result["missing"]
        assert "has healthcheck" in result["missing"]
    finally:
        _stop(ps)


def test_format_maturity_contains_expression():
    ps = _patch_all()
    _apply(ps)
    try:
        report = score_maturity(EXPR)
        text = format_maturity(report)
        assert EXPR in text
        assert "Score" in text
        assert "Grade" in text
    finally:
        _stop(ps)


@pytest.mark.parametrize("score,expected", [
    (100, "A"), (80, "A"), (79, "B"), (60, "B"),
    (59, "C"), (40, "C"), (39, "D"), (20, "D"),
    (19, "F"), (0, "F"),
])
def test_grade_boundaries(score, expected):
    assert _grade(score) == expected
