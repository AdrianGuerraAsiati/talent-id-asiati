from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4


class AttendanceEventType(StrEnum):
    CHECK_IN = "check_in"
    CHECK_OUT = "check_out"


class AttendanceMethod(StrEnum):
    FACE = "face"
    PIN = "pin"
    QR = "qr"
    MANUAL = "manual"


@dataclass(frozen=True, slots=True)
class AttendanceEvent:
    employee_id: UUID
    site_id: UUID
    device_id: UUID | None
    event_type: AttendanceEventType
    method: AttendanceMethod
    occurred_at: datetime
    idempotency_key: str
    recognition_confidence: float | None = None
    event_id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.idempotency_key.strip():
            raise ValueError("idempotency_key is required")
        if self.recognition_confidence is not None and not (
            0 <= self.recognition_confidence <= 100
        ):
            raise ValueError("recognition_confidence must be between 0 and 100")
