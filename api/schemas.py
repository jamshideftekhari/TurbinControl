from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


# --- Monitoring ---

class MeasurementsIn(BaseModel):
    wind_speed: float
    power_output: float
    rotor_rpm: float
    nacelle_temperature: float
    vibration_level: float


class RecordReadingRequest(BaseModel):
    turbine_id: str
    measurements: MeasurementsIn


class MeasurementsOut(BaseModel):
    wind_speed: float
    power_output: float
    rotor_rpm: float
    nacelle_temperature: float
    vibration_level: float


class ReadingOut(BaseModel):
    id: str
    turbine_id: str
    measurements: MeasurementsOut
    recorded_at: datetime


class AlertRuleRequest(BaseModel):
    turbine_id: str
    metric: str
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None
    severity: str = "warning"


class AlertRuleOut(BaseModel):
    id: str
    turbine_id: str
    metric: str
    threshold_min: Optional[float]
    threshold_max: Optional[float]
    severity: str


class AlertOut(BaseModel):
    id: str
    turbine_id: str
    rule_id: str
    metric: str
    value: float
    threshold: float
    severity: str
    triggered_at: datetime
    acknowledged: bool


# --- Control ---

class RegisterTurbineRequest(BaseModel):
    name: str


class TurbineOut(BaseModel):
    id: str
    name: str
    state: str
    pitch_angle: float
    yaw_angle: float
    power_setpoint: float
    created_at: datetime


class CommandOut(BaseModel):
    id: str
    turbine_id: str
    command_type: str
    parameters: Dict[str, Any]
    status: str
    issued_at: datetime
    executed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None


class SetPitchRequest(BaseModel):
    degrees: float


class SetYawRequest(BaseModel):
    degrees: float


class SetPowerRequest(BaseModel):
    kw: float


class SetMaintenanceRequest(BaseModel):
    enter: bool
