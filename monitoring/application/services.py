from typing import List, Optional

from shared.domain.value_objects import TurbineId
from ..domain.entities import Alert, AlertRule, TurbineReading
from ..domain.repositories import AlertRepository, AlertRuleRepository, ReadingRepository
from ..domain.value_objects import Measurements


class MonitoringService:
    def __init__(
        self,
        reading_repo: ReadingRepository,
        alert_repo: AlertRepository,
        rule_repo: AlertRuleRepository,
    ):
        self._readings = reading_repo
        self._alerts = alert_repo
        self._rules = rule_repo

    def record_reading(self, turbine_id: TurbineId, measurements: Measurements) -> TurbineReading:
        reading = TurbineReading.create(turbine_id, measurements)
        self._readings.save(reading)
        self._evaluate_rules(turbine_id, measurements)
        return reading

    def get_latest_reading(self, turbine_id: TurbineId) -> Optional[TurbineReading]:
        return self._readings.get_latest(turbine_id)

    def get_reading_history(self, turbine_id: TurbineId, limit: int = 100) -> List[TurbineReading]:
        return self._readings.get_history(turbine_id, limit)

    def create_alert_rule(
        self,
        turbine_id: TurbineId,
        metric: str,
        threshold_min: Optional[float],
        threshold_max: Optional[float],
        severity: str,
    ) -> AlertRule:
        rule = AlertRule.create(turbine_id, metric, threshold_min, threshold_max, severity)
        self._rules.save(rule)
        return rule

    def delete_alert_rule(self, rule_id: str) -> None:
        self._rules.delete(rule_id)

    def get_alert_rules(self, turbine_id: TurbineId) -> List[AlertRule]:
        return self._rules.get_by_turbine(turbine_id)

    def get_active_alerts(self, turbine_id: TurbineId) -> List[Alert]:
        return self._alerts.get_active(turbine_id)

    def get_all_alerts(self, turbine_id: TurbineId) -> List[Alert]:
        return self._alerts.get_all(turbine_id)

    def acknowledge_alert(self, alert_id: str) -> Optional[Alert]:
        alert = self._alerts.get_by_id(alert_id)
        if alert:
            alert.acknowledge()
            self._alerts.save(alert)
        return alert

    # --- private ---

    def _evaluate_rules(self, turbine_id: TurbineId, measurements: Measurements) -> None:
        metric_values = {
            "wind_speed": measurements.wind_speed.value,
            "power_output": measurements.power_output.value,
            "rotor_rpm": measurements.rotor_rpm.value,
            "nacelle_temperature": measurements.nacelle_temperature.value,
            "vibration_level": measurements.vibration_level.value,
        }
        for rule in self._rules.get_by_turbine(turbine_id):
            value = metric_values.get(rule.metric)
            if value is None:
                continue
            violated, threshold = self._check_threshold(value, rule)
            if violated:
                alert = Alert.create(turbine_id, rule.id, rule.metric, value, threshold, rule.severity)
                self._alerts.save(alert)

    @staticmethod
    def _check_threshold(value: float, rule: AlertRule) -> tuple[bool, float]:
        if rule.threshold_max is not None and value > rule.threshold_max:
            return True, rule.threshold_max
        if rule.threshold_min is not None and value < rule.threshold_min:
            return True, rule.threshold_min
        return False, 0.0
