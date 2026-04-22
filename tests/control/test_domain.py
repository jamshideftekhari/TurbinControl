import pytest

from control.application.services import ControlService
from control.domain.entities import Turbine
from control.domain.value_objects import CommandStatus, PitchAngle, TurbineState, YawAngle
from control.infrastructure.repositories import InMemoryCommandRepository, InMemoryTurbineRepository
from shared.domain.value_objects import TurbineId


def make_service() -> ControlService:
    return ControlService(InMemoryTurbineRepository(), InMemoryCommandRepository())


# --- Value object validation ---

def test_pitch_angle_rejects_out_of_range():
    with pytest.raises(ValueError):
        PitchAngle(91.0)
    with pytest.raises(ValueError):
        PitchAngle(-6.0)


def test_yaw_angle_rejects_out_of_range():
    with pytest.raises(ValueError):
        YawAngle(361.0)
    with pytest.raises(ValueError):
        YawAngle(-1.0)


# --- Turbine aggregate state transitions ---

def test_turbine_starts_from_stopped():
    turbine = Turbine.create("WT-1")
    assert turbine.state == TurbineState.STOPPED
    error = turbine.start()
    assert error is None
    assert turbine.state == TurbineState.RUNNING


def test_turbine_cannot_start_when_already_running():
    turbine = Turbine.create("WT-1")
    turbine.start()
    error = turbine.start()
    assert error is not None
    assert turbine.state == TurbineState.RUNNING


def test_turbine_cannot_start_in_fault_state():
    turbine = Turbine.create("WT-1")
    turbine.emergency_stop()
    error = turbine.start()
    assert error is not None
    assert turbine.state == TurbineState.FAULT


def test_turbine_cannot_start_in_maintenance():
    turbine = Turbine.create("WT-1")
    turbine.enter_maintenance()
    error = turbine.start()
    assert error is not None


def test_emergency_stop_sets_fault():
    turbine = Turbine.create("WT-1")
    turbine.start()
    turbine.emergency_stop()
    assert turbine.state == TurbineState.FAULT


def test_maintenance_requires_stopped_state():
    turbine = Turbine.create("WT-1")
    turbine.start()
    error = turbine.enter_maintenance()
    assert error is not None
    assert turbine.state == TurbineState.RUNNING


def test_exit_maintenance_goes_to_stopped():
    turbine = Turbine.create("WT-1")
    turbine.enter_maintenance()
    turbine.exit_maintenance()
    assert turbine.state == TurbineState.STOPPED


def test_power_setpoint_requires_running():
    turbine = Turbine.create("WT-1")
    from control.domain.value_objects import PowerSetpoint
    error = turbine.set_power_setpoint(PowerSetpoint(500.0))
    assert error is not None


# --- ControlService command recording ---

def test_start_command_executed():
    service = make_service()
    turbine = service.register_turbine("WT-1")
    command = service.start_turbine(turbine.id)
    assert command.status == CommandStatus.EXECUTED
    assert service.get_turbine(turbine.id).state == TurbineState.RUNNING


def test_duplicate_start_produces_rejected_command():
    service = make_service()
    turbine = service.register_turbine("WT-1")
    service.start_turbine(turbine.id)
    command = service.start_turbine(turbine.id)
    assert command.status == CommandStatus.REJECTED
    assert command.rejection_reason is not None


def test_emergency_stop_always_executes():
    service = make_service()
    turbine = service.register_turbine("WT-1")
    command = service.emergency_stop(turbine.id)
    assert command.status == CommandStatus.EXECUTED
    assert service.get_turbine(turbine.id).state == TurbineState.FAULT


def test_set_pitch_out_of_range_produces_rejected_command():
    service = make_service()
    turbine = service.register_turbine("WT-1")
    command = service.set_pitch_angle(turbine.id, 95.0)
    assert command.status == CommandStatus.REJECTED


def test_command_history_recorded():
    service = make_service()
    turbine = service.register_turbine("WT-1")
    service.start_turbine(turbine.id)
    service.stop_turbine(turbine.id)
    history = service.get_command_history(turbine.id)
    assert len(history) == 2


def test_unknown_turbine_raises():
    service = make_service()
    with pytest.raises(ValueError):
        service.start_turbine(TurbineId("does-not-exist"))
