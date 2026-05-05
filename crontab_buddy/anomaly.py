"""Detect anomalous cron expressions based on unusual scheduling patterns."""

from typing import List, NamedTuple
from crontab_buddy.recurrence import recurrence_interval_seconds, detect_recurrence
from crontab_buddy.parser import CronExpression, CronParseError


ANOMALY_REASONS = {
    "too_frequent": "Expression runs more than once per minute (step < 1)",
    "unlikely_dom_dow": "Both day-of-month and day-of-week are set, which may cause unexpected behaviour",
    "feb_30": "Month is February but day-of-month is 30 or 31, which never fires",
    "high_frequency": "Expression fires more than 60 times per hour",
    "suspicious_step": "Step value of 1 is redundant (equivalent to wildcard)",
}


class AnomalyResult(NamedTuple):
    expression: str
    anomalies: List[str]

    @property
    def ok(self) -> bool:
        return len(self.anomalies) == 0

    def __str__(self) -> str:
        if self.ok:
            return f"{self.expression}: no anomalies detected"
        joined = "; ".join(self.anomalies)
        return f"{self.expression}: {joined}"


def detect_anomalies(expression: str) -> AnomalyResult:
    """Analyse a cron expression and return any detected anomalies."""
    anomalies: List[str] = []

    try:
        expr = CronExpression(expression)
    except CronParseError as exc:
        return AnomalyResult(expression=expression, anomalies=[f"invalid expression: {exc}"])

    fields = expression.split()
    minute, hour, dom, month, dow = fields

    # High-frequency check
    try:
        interval = recurrence_interval_seconds(expression)
        if interval > 0 and interval < 60:
            anomalies.append(ANOMALY_REASONS["too_frequent"])
        elif interval > 0 and (3600 / interval) > 60:
            anomalies.append(ANOMALY_REASONS["high_frequency"])
    except Exception:
        pass

    # Redundant step-1 check
    for field in fields:
        if field.endswith("/1"):
            anomalies.append(ANOMALY_REASONS["suspicious_step"])
            break

    # DOM + DOW both set
    if dom != "*" and dow != "*":
        anomalies.append(ANOMALY_REASONS["unlikely_dom_dow"])

    # February 30/31 check
    if month in ("2", "02") and dom in ("30", "31"):
        anomalies.append(ANOMALY_REASONS["feb_30"])

    return AnomalyResult(expression=expression, anomalies=anomalies)
