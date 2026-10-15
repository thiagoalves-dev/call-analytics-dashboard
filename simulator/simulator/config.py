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
            # Average new calls per second across all accounts. 0 pauses the simulator.
            calls_per_second=float(os.environ.get("CALLS_PER_SECOND", "0.3")),
            # Share of calls sent twice, the way a telephony webhook retries.
            duplicate_delivery_rate=float(os.environ.get("DUPLICATE_DELIVERY_RATE", "0.02")),
        )
