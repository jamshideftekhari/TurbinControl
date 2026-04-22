from dataclasses import dataclass
import uuid


@dataclass(frozen=True)
class TurbineId:
    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("TurbineId cannot be empty")

    @classmethod
    def generate(cls) -> "TurbineId":
        return cls(str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value
