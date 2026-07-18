from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Contract:
    id: str

    instrument: str
    expiry: str
    strike: float

    option_type: str
    trigger_direction: str
    delta_threshold: float

    webhook_profile_id: str = ""

    # Runtime fields
    option_token: Optional[int] = None
    spot_token: Optional[int] = None

    previous_delta: Optional[float] = None
    delta: Optional[float] = None

    premium: Optional[float] = None
    spot: Optional[float] = None

    triggered: bool = False
    status: str = "IDLE"

    def to_dict(self):
        return asdict(self)