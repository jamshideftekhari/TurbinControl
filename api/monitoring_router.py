from typing import List

from fastapi import APIRouter, Depends, HTTPException

from shared.domain.value_objects import TurbineId
from monitoring.application.services import MonitoringService
from monitoring.domain.value_objects import (
    Measurements,
    PowerOutput,
    RotorRpm,
    Temperature,
    VibrationLevel,
    WindSpeed,
)
from .deps import get_monitoring_service
from .schemas import AlertOut, AlertRuleOut, AlertRuleRequest, MeasurementsOut, ReadingOut, RecordReadingRequest

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


def _to_reading_out(reading) -> ReadingOut:
    m = reading.measurements
    return ReadingOut(
        id=reading.id,
        turbine_id=reading.turbine_id.value,
        measurements=MeasurementsOut(
            wind_speed=m.wind_speed.value,
            power_output=m.power_output.value,
            rotor_rpm=m.rotor_rpm.value,
            nacelle_temperature=m.nacelle_temperature.value,
            vibration_level=m.vibration_level.value,
        ),
        recorded_at=reading.recorded_at,
    )


def _to_alert_out(alert) -> AlertOut:
    return AlertOut(
        id=alert.id,
        turbine_id=alert.turbine_id.value,
        rule_id=alert.rule_id,
        metric=alert.metric,
        value=alert.value,
        threshold=alert.threshold,
        severity=alert.severity,
        triggered_at=alert.triggered_at,
        acknowledged=alert.acknowledged,
    )


@router.post("/readings", response_model=ReadingOut, status_code=201)
def record_reading(
    body: RecordReadingRequest,
    service: MonitoringService = Depends(get_monitoring_service),
):
    try:
        m = body.measurements
        measurements = Measurements(
            wind_speed=WindSpeed(m.wind_speed),
            power_output=PowerOutput(m.power_output),
            rotor_rpm=RotorRpm(m.rotor_rpm),
            nacelle_temperature=Temperature(m.nacelle_temperature),
            vibration_level=VibrationLevel(m.vibration_level),
        )
        reading = service.record_reading(TurbineId(body.turbine_id), measurements)
        return _to_reading_out(reading)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/turbines/{turbine_id}/readings/latest", response_model=ReadingOut)
def get_latest_reading(
    turbine_id: str,
    service: MonitoringService = Depends(get_monitoring_service),
):
    reading = service.get_latest_reading(TurbineId(turbine_id))
    if not reading:
        raise HTTPException(status_code=404, detail="No readings found for this turbine")
    return _to_reading_out(reading)


@router.get("/turbines/{turbine_id}/readings", response_model=List[ReadingOut])
def get_reading_history(
    turbine_id: str,
    limit: int = 100,
    service: MonitoringService = Depends(get_monitoring_service),
):
    readings = service.get_reading_history(TurbineId(turbine_id), limit)
    return [_to_reading_out(r) for r in readings]


@router.post("/rules", response_model=AlertRuleOut, status_code=201)
def create_alert_rule(
    body: AlertRuleRequest,
    service: MonitoringService = Depends(get_monitoring_service),
):
    rule = service.create_alert_rule(
        TurbineId(body.turbine_id),
        body.metric,
        body.threshold_min,
        body.threshold_max,
        body.severity,
    )
    return AlertRuleOut(
        id=rule.id,
        turbine_id=rule.turbine_id.value,
        metric=rule.metric,
        threshold_min=rule.threshold_min,
        threshold_max=rule.threshold_max,
        severity=rule.severity,
    )


@router.get("/turbines/{turbine_id}/rules", response_model=List[AlertRuleOut])
def get_alert_rules(
    turbine_id: str,
    service: MonitoringService = Depends(get_monitoring_service),
):
    rules = service.get_alert_rules(TurbineId(turbine_id))
    return [
        AlertRuleOut(
            id=r.id,
            turbine_id=r.turbine_id.value,
            metric=r.metric,
            threshold_min=r.threshold_min,
            threshold_max=r.threshold_max,
            severity=r.severity,
        )
        for r in rules
    ]


@router.delete("/rules/{rule_id}", status_code=204)
def delete_alert_rule(
    rule_id: str,
    service: MonitoringService = Depends(get_monitoring_service),
):
    service.delete_alert_rule(rule_id)


@router.get("/turbines/{turbine_id}/alerts", response_model=List[AlertOut])
def get_alerts(
    turbine_id: str,
    active_only: bool = True,
    service: MonitoringService = Depends(get_monitoring_service),
):
    if active_only:
        alerts = service.get_active_alerts(TurbineId(turbine_id))
    else:
        alerts = service.get_all_alerts(TurbineId(turbine_id))
    return [_to_alert_out(a) for a in alerts]


@router.post("/alerts/{alert_id}/acknowledge", response_model=AlertOut)
def acknowledge_alert(
    alert_id: str,
    service: MonitoringService = Depends(get_monitoring_service),
):
    alert = service.acknowledge_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return _to_alert_out(alert)
