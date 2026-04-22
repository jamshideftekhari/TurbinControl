from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
import uuid

from shared.domain.value_objects import TurbineId
from .value_objects import Measurements


@dataclass
class TurbineReading:
    id: str
    turbine_id: TurbineId
    measurements: Measurements
    recorded_at: datetime

    @classmethod
    def create(cls, turbine_id: TurbineId, measurements: Measurements) -> "TurbineReading":
        return cls(
            id=str(uuid.uuid4()),
            turbine_id=turbine_id,
            measurements=measurements,
            recorded_at=datetime.now(timezone.utc),
        )


@dataclass
class AlertRule:
    id: str
    turbine_id: TurbineId
    metric: str
    threshold_min: Optional[float]
    threshold_max: Optional[float]
    severity: str  # "warning" | "critical"

    @classmethod
    def create(
        cls,
        turbine_id: TurbineId,
        metric: str,
        threshold_min: Optional[float],
        threshold_max: Optional[float],
        severity: str,
    ) -> "AlertRule":
        return cls(
            id=str(uuid.uuid4()),
            turbine_id=turbine_id,
            metric=metric,
            threshold_min=threshold_min,
            threshold_max=threshold_max,
            severity=severity,
        )


@dataclass
class Alert:
    id: str
    turbine_id: TurbineId
    rule_id: str
    metric: str
    value: float
    threshold: float
    severity: str
    triggered_at: datetime
    acknowledged: bool = False

    @classmethod
    def create(
        cls,
        turbine_id: TurbineId,
        rule_id: str,
        metric: str,
        value: float,
        threshold: float,
        severity: str,
    ) -> "Alert":
        return cls(
            id=str(uuid.uuid4()),
            turbine_id=turbine_id,
            rule_id=rule_id,
            metric=metric,
            value=value,
            threshold=threshold,
            severity=severity,
            triggered_at=datetime.now(timezone.utc),
        )

    def acknowledge(self) -> None:
        self.acknowledged = True
