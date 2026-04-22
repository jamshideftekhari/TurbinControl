from monitoring.application.services import MonitoringService
from monitoring.infrastructure.repositories import (
    InMemoryAlertRepository,
    InMemoryAlertRuleRepository,
    InMemoryReadingRepository,
)
from control.application.services import ControlService
from control.infrastructure.repositories import InMemoryCommandRepository, InMemoryTurbineRepository

# Singleton in-memory stores — replaced by real DB adapters in production
_reading_repo = InMemoryReadingRepository()
_alert_repo = InMemoryAlertRepository()
_rule_repo = InMemoryAlertRuleRepository()
_turbine_repo = InMemoryTurbineRepository()
_command_repo = InMemoryCommandRepository()


def get_monitoring_service() -> MonitoringService:
    return MonitoringService(_reading_repo, _alert_repo, _rule_repo)


def get_control_service() -> ControlService:
    return ControlService(_turbine_repo, _command_repo)
