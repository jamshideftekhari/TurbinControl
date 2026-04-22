from typing import List

from fastapi import APIRouter, Depends, HTTPException

from shared.domain.value_objects import TurbineId
from control.application.services import ControlService
from .deps import get_control_service
from .schemas import (
    CommandOut,
    RegisterTurbineRequest,
    SetMaintenanceRequest,
    SetPitchRequest,
    SetPowerRequest,
    SetYawRequest,
    TurbineOut,
)

router = APIRouter(prefix="/control", tags=["control"])


def _to_turbine_out(turbine) -> TurbineOut:
    return TurbineOut(
        id=turbine.id.value,
        name=turbine.name,
        state=turbine.state.value,
        pitch_angle=turbine.pitch_angle.degrees,
        yaw_angle=turbine.yaw_angle.degrees,
        power_setpoint=turbine.power_setpoint.kw,
        created_at=turbine.created_at,
    )


def _to_command_out(command) -> CommandOut:
    return CommandOut(
        id=command.id,
        turbine_id=command.turbine_id.value,
        command_type=command.command_type.value,
        parameters=command.parameters,
        status=command.status.value,
        issued_at=command.issued_at,
        executed_at=command.executed_at,
        rejection_reason=command.rejection_reason,
    )


@router.post("/turbines", response_model=TurbineOut, status_code=201)
def register_turbine(
    body: RegisterTurbineRequest,
    service: ControlService = Depends(get_control_service),
):
    turbine = service.register_turbine(body.name)
    return _to_turbine_out(turbine)


@router.get("/turbines", response_model=List[TurbineOut])
def list_turbines(service: ControlService = Depends(get_control_service)):
    return [_to_turbine_out(t) for t in service.list_turbines()]


@router.get("/turbines/{turbine_id}", response_model=TurbineOut)
def get_turbine(turbine_id: str, service: ControlService = Depends(get_control_service)):
    turbine = service.get_turbine(TurbineId(turbine_id))
    if not turbine:
        raise HTTPException(status_code=404, detail="Turbine not found")
    return _to_turbine_out(turbine)


@router.post("/turbines/{turbine_id}/start", response_model=CommandOut)
def start_turbine(turbine_id: str, service: ControlService = Depends(get_control_service)):
    try:
        return _to_command_out(service.start_turbine(TurbineId(turbine_id)))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/turbines/{turbine_id}/stop", response_model=CommandOut)
def stop_turbine(turbine_id: str, service: ControlService = Depends(get_control_service)):
    try:
        return _to_command_out(service.stop_turbine(TurbineId(turbine_id)))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/turbines/{turbine_id}/emergency-stop", response_model=CommandOut)
def emergency_stop(turbine_id: str, service: ControlService = Depends(get_control_service)):
    try:
        return _to_command_out(service.emergency_stop(TurbineId(turbine_id)))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/turbines/{turbine_id}/pitch", response_model=CommandOut)
def set_pitch(
    turbine_id: str,
    body: SetPitchRequest,
    service: ControlService = Depends(get_control_service),
):
    try:
        return _to_command_out(service.set_pitch_angle(TurbineId(turbine_id), body.degrees))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/turbines/{turbine_id}/yaw", response_model=CommandOut)
def set_yaw(
    turbine_id: str,
    body: SetYawRequest,
    service: ControlService = Depends(get_control_service),
):
    try:
        return _to_command_out(service.set_yaw_angle(TurbineId(turbine_id), body.degrees))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/turbines/{turbine_id}/power-setpoint", response_model=CommandOut)
def set_power_setpoint(
    turbine_id: str,
    body: SetPowerRequest,
    service: ControlService = Depends(get_control_service),
):
    try:
        return _to_command_out(service.set_power_setpoint(TurbineId(turbine_id), body.kw))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/turbines/{turbine_id}/maintenance", response_model=CommandOut)
def set_maintenance(
    turbine_id: str,
    body: SetMaintenanceRequest,
    service: ControlService = Depends(get_control_service),
):
    try:
        return _to_command_out(service.set_maintenance_mode(TurbineId(turbine_id), body.enter))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/turbines/{turbine_id}/commands", response_model=List[CommandOut])
def get_command_history(turbine_id: str, service: ControlService = Depends(get_control_service)):
    commands = service.get_command_history(TurbineId(turbine_id))
    return [_to_command_out(c) for c in commands]
