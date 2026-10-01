from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from talent_id.modules.attendance.domain import AttendanceEventType, AttendanceMethod


class AttendanceEventResponse(BaseModel):
    id: UUID
    employee_id: UUID
    site_id: UUID
    device_id: UUID | None
    event_type: AttendanceEventType
    method: AttendanceMethod
    occurred_at: datetime
    idempotency_key: str
    recognition_confidence: float | None
    created: bool
