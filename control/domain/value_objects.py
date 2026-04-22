from dataclasses import dataclass
from enum import Enum


class TurbineState(str, Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    FAULT = "fault"
    MAINTENANCE = "maintenance"


class CommandType(str, Enum):
    START = "start"
    STOP = "stop"
    EMERGENCY_STOP = "emergency_stop"
    SET_PITCH = "set_pitch"
    SET_YAW = "set_yaw"
    SET_POWER_SETPOINT = "set_power_setpoint"
    SET_MAINTENANCE = "set_maintenance"


class CommandStatus(str, Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    REJECTED = "rejected"


@dataclass(frozen=True)
class PitchAngle:
    degrees: float  # -5 to 90

    def __post_init__(self):
        if not (-5 <= self.degrees <= 90):
            raise ValueError(f"Pitch angle must be between -5 and 90 degrees, got {self.degrees}")


@dataclass(frozen=True)
class YawAngle:
    degrees: float  # 0 to 360

    def __post_init__(self):
        if not (0 <= self.degrees <= 360):
            raise ValueError(f"Yaw angle must be between 0 and 360 degrees, got {self.degrees}")


@dataclass(frozen=True)
class PowerSetpoint:
    kw: float

    def __post_init__(self):
        if self.kw < 0:
            raise ValueError("Power setpoint cannot be negative")
