from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ReadingRecorded:
    turbine_id: str
    reading_id: str
    occurred_at: datetime


@dataclass(frozen=True)
class AlertTriggered:
    turbine_id: str
    alert_id: str
    metric: str
    severity: str
    occurred_at: datetime
