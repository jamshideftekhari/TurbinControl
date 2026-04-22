from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TurbineRegistered:
    turbine_id: str
    name: str
    occurred_at: datetime


@dataclass(frozen=True)
class CommandIssued:
    turbine_id: str
    command_id: str
    command_type: str
    occurred_at: datetime


@dataclass(frozen=True)
class TurbineStateChanged:
    turbine_id: str
    previous_state: str
    new_state: str
    occurred_at: datetime
