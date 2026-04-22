from dataclasses import dataclass


@dataclass(frozen=True)
class WindSpeed:
    value: float  # m/s

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Wind speed cannot be negative")


@dataclass(frozen=True)
class PowerOutput:
    value: float  # kW


@dataclass(frozen=True)
class RotorRpm:
    value: float

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Rotor RPM cannot be negative")


@dataclass(frozen=True)
class Temperature:
    value: float  # Celsius


@dataclass(frozen=True)
class VibrationLevel:
    value: float  # g (acceleration)

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Vibration level cannot be negative")


@dataclass(frozen=True)
class Measurements:
    wind_speed: WindSpeed
    power_output: PowerOutput
    rotor_rpm: RotorRpm
    nacelle_temperature: Temperature
    vibration_level: VibrationLevel
