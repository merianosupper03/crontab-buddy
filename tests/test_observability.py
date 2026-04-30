"""Tests for crontab_buddy.observability."""

import pytest
from crontab_buddy.observability import (
    delete_observability,
    get_observability,
    list_observability,
    set_observability,
)


@pytest.fixture
def tmp_obs(tmp_path):
    return str(tmp_path / "obs.json")


def test_set_and_get(tmp_obs):
    set_observability("0 * * * *", path=tmp_obs)
    cfg = get_observability("0 * * * *", path=tmp_obs)
    assert cfg is not None
    assert cfg["log_level"] == "info"
    assert cfg["trace_backend"] == "none"
    assert cfg["metrics_enabled"] is False


def test_get_missing_returns_none(tmp_obs):
    assert get_observability("* * * * *", path=tmp_obs) is None


def test_invalid_log_level_raises(tmp_obs):
    with pytest.raises(ValueError, match="log_level"):
        set_observability("* * * * *", log_level="verbose", path=tmp_obs)


def test_invalid_trace_backend_raises(tmp_obs):
    with pytest.raises(ValueError, match="trace_backend"):
        set_observability("* * * * *", trace_backend="datadog", path=tmp_obs)


def test_overwrite_observability(tmp_obs):
    set_observability("0 * * * *", log_level="debug", path=tmp_obs)
    set_observability("0 * * * *", log_level="error", path=tmp_obs)
    cfg = get_observability("0 * * * *", path=tmp_obs)
    assert cfg["log_level"] == "error"


def test_metrics_enabled(tmp_obs):
    set_observability("5 4 * * *", metrics_enabled=True, path=tmp_obs)
    cfg = get_observability("5 4 * * *", path=tmp_obs)
    assert cfg["metrics_enabled"] is True


def test_delete_existing(tmp_obs):
    set_observability("0 0 * * *", path=tmp_obs)
    result = delete_observability("0 0 * * *", path=tmp_obs)
    assert result is True
    assert get_observability("0 0 * * *", path=tmp_obs) is None


def test_delete_missing_returns_false(tmp_obs):
    assert delete_observability("1 2 3 4 5", path=tmp_obs) is False


def test_list_all(tmp_obs):
    set_observability("0 * * * *", log_level="debug", path=tmp_obs)
    set_observability("5 4 * * *", trace_backend="jaeger", path=tmp_obs)
    configs = list_observability(path=tmp_obs)
    assert "0 * * * *" in configs
    assert "5 4 * * *" in configs


def test_list_empty(tmp_obs):
    assert list_observability(path=tmp_obs) == {}


def test_trace_backend_stored(tmp_obs):
    set_observability("*/5 * * * *", trace_backend="otlp", path=tmp_obs)
    cfg = get_observability("*/5 * * * *", path=tmp_obs)
    assert cfg["trace_backend"] == "otlp"
