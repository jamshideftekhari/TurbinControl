from dataclasses import dataclass # field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid

from shared.domain.value_objects import TurbineId
from .value_objects import CommandStatus, CommandType, PitchAngle, PowerSetpoint, TurbineState, YawAngle


@dataclass
class ControlCommand:
    id: str
    turbine_id: TurbineId
    command_type: CommandType
    parameters: Dict[str, Any]
    status: CommandStatus
    issued_at: datetime
    executed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

    @classmethod
    def create(
        cls,
        turbine_id: TurbineId,
        command_type: CommandType,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> "ControlCommand":
        return cls(
            id=str(uuid.uuid4()),
            turbine_id=turbine_id,
            command_type=command_type,
            parameters=parameters or {},
            status=CommandStatus.PENDING,
            issued_at=datetime.now(timezone.utc),
        )

    def execute(self) -> None:
        self.status = CommandStatus.EXECUTED
        self.executed_at = datetime.now(timezone.utc)

    def reject(self, reason: str) -> None:
        self.status = CommandStatus.REJECTED
        self.rejection_reason = reason


@dataclass
class Turbine:
    id: TurbineId
    name: str
    state: TurbineState
    pitch_angle: PitchAngle
    yaw_angle: YawAngle
    power_setpoint: PowerSetpoint
    created_at: datetime

    @classmethod
    def create(cls, name: str) -> "Turbine":
        return cls(
            id=TurbineId.generate(),
            name=name,
            state=TurbineState.STOPPED,
            pitch_angle=PitchAngle(0.0),
            yaw_angle=YawAngle(0.0),
            power_setpoint=PowerSetpoint(0.0),
            created_at=datetime.now(timezone.utc),
        )

    def start(self) -> Optional[str]:
        if self.state == TurbineState.RUNNING:
            return "Turbine is already running"
        if self.state == TurbineState.FAULT:
            return "Cannot start a turbine in fault state — clear the fault first"
        if self.state == TurbineState.MAINTENANCE:
            return "Cannot start a turbine in maintenance mode"
        self.state = TurbineState.RUNNING
        return None

    def stop(self) -> Optional[str]:
        if self.state == TurbineState.STOPPED:
            return "Turbine is already stopped"
        self.state = TurbineState.STOPPED
        return None

    def emergency_stop(self) -> None:
        self.state = TurbineState.FAULT

    def set_pitch(self, angle: PitchAngle) -> Optional[str]:
        if self.state not in (TurbineState.RUNNING, TurbineState.STOPPED):
            return f"Cannot adjust pitch while in state '{self.state}'"
        self.pitch_angle = angle
        return None

    def set_yaw(self, angle: YawAngle) -> Optional[str]:
        if self.state not in (TurbineState.RUNNING, TurbineState.STOPPED):
            return f"Cannot adjust yaw while in state '{self.state}'"
        self.yaw_angle = angle
        return None

    def set_power_setpoint(self, setpoint: PowerSetpoint) -> Optional[str]:
        if self.state != TurbineState.RUNNING:
            return "Can only set power setpoint while turbine is running"
        self.power_setpoint = setpoint
        return None

    def enter_maintenance(self) -> Optional[str]:
        if self.state == TurbineState.RUNNING:
            return "Stop the turbine before entering maintenance mode"
        self.state = TurbineState.MAINTENANCE
        return None

    def exit_maintenance(self) -> None:
        if self.state == TurbineState.MAINTENANCE:
            self.state = TurbineState.STOPPED
