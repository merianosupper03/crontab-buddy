"""CLI commands for resilience scoring."""

from crontab_buddy.resilience import score_resilience
from crontab_buddy.recurrence import is_high_frequency


def _bool_flag(val) -> bool:
    if isinstance(val, bool):
        return val
    return str(val).lower() in ("1", "true", "yes")


def cmd_resilience_score(args, print_fn=print):
    """Score the resilience of a cron expression."""
    try:
        high_freq = is_high_frequency(args.expression)
    except Exception:
        high_freq = None

    result = score_resilience(
        expression=args.expression,
        has_retry=_bool_flag(getattr(args, "retry", False)),
        has_healthcheck=_bool_flag(getattr(args, "healthcheck", False)),
        has_timeout=_bool_flag(getattr(args, "timeout", False)),
        has_lock=_bool_flag(getattr(args, "lock", False)),
        has_notify=_bool_flag(getattr(args, "notify", False)),
        is_high_frequency=high_freq,
    )
    print_fn(str(result))


def cmd_resilience_score_json(args, print_fn=print):
    """Output resilience score as JSON."""
    import json
    try:
        high_freq = is_high_frequency(args.expression)
    except Exception:
        high_freq = None

    result = score_resilience(
        expression=args.expression,
        has_retry=_bool_flag(getattr(args, "retry", False)),
        has_healthcheck=_bool_flag(getattr(args, "healthcheck", False)),
        has_timeout=_bool_flag(getattr(args, "timeout", False)),
        has_lock=_bool_flag(getattr(args, "lock", False)),
        has_notify=_bool_flag(getattr(args, "notify", False)),
        is_high_frequency=high_freq,
    )
    print_fn(json.dumps({
        "expression": result.expression,
        "score": result.score,
        "grade": result.grade,
        "factors": result.factors,
        "suggestions": result.suggestions,
    }, indent=2))
