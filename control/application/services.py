from typing import List, Optional

from shared.domain.value_objects import TurbineId
from ..domain.entities import ControlCommand, Turbine
from ..domain.repositories import CommandRepository, TurbineRepository
from ..domain.value_objects import CommandType, PitchAngle, PowerSetpoint, YawAngle


class ControlService:
    def __init__(self, turbine_repo: TurbineRepository, command_repo: CommandRepository):
        self._turbines = turbine_repo
        self._commands = command_repo

    def register_turbine(self, name: str) -> Turbine:
        turbine = Turbine.create(name)
        self._turbines.save(turbine)
        return turbine

    def get_turbine(self, turbine_id: TurbineId) -> Optional[Turbine]:
        return self._turbines.get_by_id(turbine_id)

    def list_turbines(self) -> List[Turbine]:
        return self._turbines.get_all()

    def start_turbine(self, turbine_id: TurbineId) -> ControlCommand:
        turbine = self._require_turbine(turbine_id)
        command = ControlCommand.create(turbine_id, CommandType.START)
        error = turbine.start()
        if error:
            command.reject(error)
        else:
            command.execute()
            self._turbines.save(turbine)
        self._commands.save(command)
        return command

    def stop_turbine(self, turbine_id: TurbineId) -> ControlCommand:
        turbine = self._require_turbine(turbine_id)
        command = ControlCommand.create(turbine_id, CommandType.STOP)
        error = turbine.stop()
        if error:
            command.reject(error)
        else:
            command.execute()
            self._turbines.save(turbine)
        self._commands.save(command)
        return command

    def emergency_stop(self, turbine_id: TurbineId) -> ControlCommand:
        turbine = self._require_turbine(turbine_id)
        command = ControlCommand.create(turbine_id, CommandType.EMERGENCY_STOP)
        turbine.emergency_stop()
        command.execute()
        self._turbines.save(turbine)
        self._commands.save(command)
        return command

    def set_pitch_angle(self, turbine_id: TurbineId, degrees: float) -> ControlCommand:
        turbine = self._require_turbine(turbine_id)
        command = ControlCommand.create(turbine_id, CommandType.SET_PITCH, {"degrees": degrees})
        try:
            angle = PitchAngle(degrees)
        except ValueError as e:
            command.reject(str(e))
            self._commands.save(command)
            return command
        error = turbine.set_pitch(angle)
        if error:
            command.reject(error)
        else:
            command.execute()
            self._turbines.save(turbine)
        self._commands.save(command)
        return command

    def set_yaw_angle(self, turbine_id: TurbineId, degrees: float) -> ControlCommand:
        turbine = self._require_turbine(turbine_id)
        command = ControlCommand.create(turbine_id, CommandType.SET_YAW, {"degrees": degrees})
        try:
            angle = YawAngle(degrees)
        except ValueError as e:
            command.reject(str(e))
            self._commands.save(command)
            return command
        error = turbine.set_yaw(angle)
        if error:
            command.reject(error)
        else:
            command.execute()
            self._turbines.save(turbine)
        self._commands.save(command)
        return command

    def set_power_setpoint(self, turbine_id: TurbineId, kw: float) -> ControlCommand:
        turbine = self._require_turbine(turbine_id)
        command = ControlCommand.create(turbine_id, CommandType.SET_POWER_SETPOINT, {"kw": kw})
        try:
            setpoint = PowerSetpoint(kw)
        except ValueError as e:
            command.reject(str(e))
            self._commands.save(command)
            return command
        error = turbine.set_power_setpoint(setpoint)
        if error:
            command.reject(error)
        else:
            command.execute()
            self._turbines.save(turbine)
        self._commands.save(command)
        return command

    def set_maintenance_mode(self, turbine_id: TurbineId, enter: bool) -> ControlCommand:
        turbine = self._require_turbine(turbine_id)
        command = ControlCommand.create(turbine_id, CommandType.SET_MAINTENANCE, {"enter": enter})
        if enter:
            error = turbine.enter_maintenance()
        else:
            turbine.exit_maintenance()
            error = None
        if error:
            command.reject(error)
        else:
            command.execute()
            self._turbines.save(turbine)
        self._commands.save(command)
        return command

    def get_command_history(self, turbine_id: TurbineId) -> List[ControlCommand]:
        return self._commands.get_by_turbine(turbine_id)

    def _require_turbine(self, turbine_id: TurbineId) -> Turbine:
        turbine = self._turbines.get_by_id(turbine_id)
        if not turbine:
            raise ValueError(f"Turbine '{turbine_id}' not found")
        return turbine
