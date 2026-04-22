from abc import ABC, abstractmethod
from typing import List, Optional

from shared.domain.value_objects import TurbineId
from .entities import ControlCommand, Turbine


class TurbineRepository(ABC):
    @abstractmethod
    def save(self, turbine: Turbine) -> None: ...

    @abstractmethod
    def get_by_id(self, turbine_id: TurbineId) -> Optional[Turbine]: ...

    @abstractmethod
    def get_all(self) -> List[Turbine]: ...

    @abstractmethod
    def delete(self, turbine_id: TurbineId) -> None: ...


class CommandRepository(ABC):
    @abstractmethod
    def save(self, command: ControlCommand) -> None: ...

    @abstractmethod
    def get_by_id(self, command_id: str) -> Optional[ControlCommand]: ...

    @abstractmethod
    def get_by_turbine(self, turbine_id: TurbineId) -> List[ControlCommand]: ...
