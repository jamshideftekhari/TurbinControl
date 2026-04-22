from typing import Dict, List, Optional

from shared.domain.value_objects import TurbineId
from ..domain.entities import Alert, AlertRule, TurbineReading
from ..domain.repositories import AlertRepository, AlertRuleRepository, ReadingRepository


class InMemoryReadingRepository(ReadingRepository):
    def __init__(self):
        self._store: Dict[str, List[TurbineReading]] = {}

    def save(self, reading: TurbineReading) -> None:
        self._store.setdefault(reading.turbine_id.value, []).append(reading)

    def get_latest(self, turbine_id: TurbineId) -> Optional[TurbineReading]:
        readings = self._store.get(turbine_id.value, [])
        return readings[-1] if readings else None

    def get_history(self, turbine_id: TurbineId, limit: int = 100) -> List[TurbineReading]:
        readings = self._store.get(turbine_id.value, [])
        return list(reversed(readings[-limit:]))


class InMemoryAlertRepository(AlertRepository):
    def __init__(self):
        self._store: Dict[str, Alert] = {}

    def save(self, alert: Alert) -> None:
        self._store[alert.id] = alert

    def get_by_id(self, alert_id: str) -> Optional[Alert]:
        return self._store.get(alert_id)

    def get_active(self, turbine_id: TurbineId) -> List[Alert]:
        return [a for a in self._store.values() if a.turbine_id.value == turbine_id.value and not a.acknowledged]

    def get_all(self, turbine_id: TurbineId) -> List[Alert]:
        return [a for a in self._store.values() if a.turbine_id.value == turbine_id.value]


class InMemoryAlertRuleRepository(AlertRuleRepository):
    def __init__(self):
        self._store: Dict[str, AlertRule] = {}

    def save(self, rule: AlertRule) -> None:
        self._store[rule.id] = rule

    def get_by_id(self, rule_id: str) -> Optional[AlertRule]:
        return self._store.get(rule_id)

    def get_by_turbine(self, turbine_id: TurbineId) -> List[AlertRule]:
        return [r for r in self._store.values() if r.turbine_id.value == turbine_id.value]

    def delete(self, rule_id: str) -> None:
        self._store.pop(rule_id, None)
