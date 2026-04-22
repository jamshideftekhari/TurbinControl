from abc import ABC, abstractmethod
from typing import List, Optional

from shared.domain.value_objects import TurbineId
from .entities import Alert, AlertRule, TurbineReading


class ReadingRepository(ABC):
    @abstractmethod
    def save(self, reading: TurbineReading) -> None: ...

    @abstractmethod
    def get_latest(self, turbine_id: TurbineId) -> Optional[TurbineReading]: ...

    @abstractmethod
    def get_history(self, turbine_id: TurbineId, limit: int = 100) -> List[TurbineReading]: ...


class AlertRepository(ABC):
    @abstractmethod
    def save(self, alert: Alert) -> None: ...

    @abstractmethod
    def get_by_id(self, alert_id: str) -> Optional[Alert]: ...

    @abstractmethod
    def get_active(self, turbine_id: TurbineId) -> List[Alert]: ...

    @abstractmethod
    def get_all(self, turbine_id: TurbineId) -> List[Alert]: ...


class AlertRuleRepository(ABC):
    @abstractmethod
    def save(self, rule: AlertRule) -> None: ...

    @abstractmethod
    def get_by_id(self, rule_id: str) -> Optional[AlertRule]: ...

    @abstractmethod
    def get_by_turbine(self, turbine_id: TurbineId) -> List[AlertRule]: ...

    @abstractmethod
    def delete(self, rule_id: str) -> None: ...
