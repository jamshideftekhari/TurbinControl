import pytest

from shared.domain.value_objects import TurbineId
from monitoring.domain.value_objects import (
    Measurements, WindSpeed, PowerOutput, RotorRpm, Temperature, VibrationLevel,
)
from monitoring.domain.entities import Alert, AlertRule, TurbineReading
from monitoring.application.services import MonitoringService
from monitoring.infrastructure.repositories import (
    InMemoryAlertRepository, InMemoryAlertRuleRepository, InMemoryReadingRepository,
)


def make_measurements(wind_speed=10.0, power_output=1000.0, rotor_rpm=12.0,
                       nacelle_temperature=40.0, vibration_level=0.2) -> Measurements:
    return Measurements(
        wind_speed=WindSpeed(wind_speed),
        power_output=PowerOutput(power_output),
        rotor_rpm=RotorRpm(rotor_rpm),
        nacelle_temperature=Temperature(nacelle_temperature),
        vibration_level=VibrationLevel(vibration_level),
    )


def make_service() -> MonitoringService:
    return MonitoringService(
        InMemoryReadingRepository(),
        InMemoryAlertRepository(),
        InMemoryAlertRuleRepository(),
    )


# --- Value object validation ---

def test_wind_speed_rejects_negative():
    with pytest.raises(ValueError):
        WindSpeed(-1.0)


def test_rotor_rpm_rejects_negative():
    with pytest.raises(ValueError):
        RotorRpm(-5.0)


def test_vibration_level_rejects_negative():
    with pytest.raises(ValueError):
        VibrationLevel(-0.1)


# --- Reading ---

def test_record_reading_stores_and_returns():
    service = make_service()
    turbine_id = TurbineId("t-001")
    reading = service.record_reading(turbine_id, make_measurements())
    assert reading.turbine_id == turbine_id
    assert service.get_latest_reading(turbine_id) == reading


def test_history_is_most_recent_first():
    service = make_service()
    turbine_id = TurbineId("t-001")
    service.record_reading(turbine_id, make_measurements(wind_speed=5.0))
    service.record_reading(turbine_id, make_measurements(wind_speed=15.0))
    history = service.get_reading_history(turbine_id)
    assert history[0].measurements.wind_speed.value == 15.0


def test_latest_returns_none_for_unknown_turbine():
    service = make_service()
    assert service.get_latest_reading(TurbineId("unknown")) is None


# --- Alert rules ---

def test_alert_fired_when_max_threshold_exceeded():
    service = make_service()
    turbine_id = TurbineId("t-001")
    service.create_alert_rule(turbine_id, "wind_speed", None, 25.0, "warning")
    service.record_reading(turbine_id, make_measurements(wind_speed=30.0))
    alerts = service.get_active_alerts(turbine_id)
    assert len(alerts) == 1
    assert alerts[0].metric == "wind_speed"
    assert alerts[0].severity == "warning"


def test_alert_fired_when_min_threshold_breached():
    service = make_service()
    turbine_id = TurbineId("t-001")
    service.create_alert_rule(turbine_id, "rotor_rpm", 5.0, None, "critical")
    service.record_reading(turbine_id, make_measurements(rotor_rpm=2.0))
    alerts = service.get_active_alerts(turbine_id)
    assert len(alerts) == 1
    assert alerts[0].severity == "critical"


def test_no_alert_when_within_threshold():
    service = make_service()
    turbine_id = TurbineId("t-001")
    service.create_alert_rule(turbine_id, "wind_speed", None, 25.0, "warning")
    service.record_reading(turbine_id, make_measurements(wind_speed=20.0))
    assert service.get_active_alerts(turbine_id) == []


def test_acknowledge_clears_active_alert():
    service = make_service()
    turbine_id = TurbineId("t-001")
    service.create_alert_rule(turbine_id, "wind_speed", None, 25.0, "warning")
    service.record_reading(turbine_id, make_measurements(wind_speed=30.0))
    alert_id = service.get_active_alerts(turbine_id)[0].id
    service.acknowledge_alert(alert_id)
    assert service.get_active_alerts(turbine_id) == []
