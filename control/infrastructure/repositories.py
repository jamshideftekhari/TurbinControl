from typing import Dict, List, Optional

from shared.domain.value_objects import TurbineId
from ..domain.entities import ControlCommand, Turbine
from ..domain.repositories import CommandRepository, TurbineRepository


class InMemoryTurbineRepository(TurbineRepository):
    def __init__(self):
        self._store: Dict[str, Turbine] = {}

    def save(self, turbine: Turbine) -> None:
        self._store[turbine.id.value] = turbine

    def get_by_id(self, turbine_id: TurbineId) -> Optional[Turbine]:
        return self._store.get(turbine_id.value)

    def get_all(self) -> List[Turbine]:
        return list(self._store.values())

    def delete(self, turbine_id: TurbineId) -> None:
        self._store.pop(turbine_id.value, None)


class InMemoryCommandRepository(CommandRepository):
    def __init__(self):
        self._store: Dict[str, ControlCommand] = {}

    def save(self, command: ControlCommand) -> None:
        self._store[command.id] = command

    def get_by_id(self, command_id: str) -> Optional[ControlCommand]:
        return self._store.get(command_id)

    def get_by_turbine(self, turbine_id: TurbineId) -> List[ControlCommand]:
        return [c for c in self._store.values() if c.turbine_id.value == turbine_id.value]
