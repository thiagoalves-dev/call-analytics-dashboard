import os
from dataclasses import dataclass


@dataclass(frozen=True)
class SimulatorConfig:
    api_url: str
    api_keys: tuple[str, ...]
    calls_per_second: float
    duplicate_delivery_rate: float

    @classmethod
    def from_environment(cls) -> "SimulatorConfig":
        return cls(
            api_url=os.environ.get("API_URL", "http://localhost:1012"),
            api_keys=tuple(key for key in os.environ.get("API_KEYS", "").split(",") if key),
            calls_per_second=float(os.environ.get("CALLS_PER_SECOND", "0.3")),
            duplicate_delivery_rate=float(os.environ.get("DUPLICATE_DELIVERY_RATE", "0.02")),
        )
