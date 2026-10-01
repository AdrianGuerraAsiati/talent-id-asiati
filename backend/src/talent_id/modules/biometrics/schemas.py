from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from talent_id.modules.attendance.schemas import AttendanceEventResponse


class BiometricEnrollmentResponse(BaseModel):
    employee_id: UUID
    provider: str
    face_count: int
    active: bool
    enrolled_at: datetime


class KioskRecognitionResponse(BaseModel):
    employee_id: UUID
    display_name: str
    similarity: float
    attendance: AttendanceEventResponse
