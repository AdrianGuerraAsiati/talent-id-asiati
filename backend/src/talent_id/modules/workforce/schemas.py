from datetime import time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from talent_id.modules.workforce.domain import EmployeeStatus


class SiteCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    code: str | None = Field(default=None, max_length=32)
    timezone: str = Field(default="America/Bogota", min_length=1, max_length=64)


class SiteResponse(BaseModel):
    id: UUID
    name: str
    code: str | None
    timezone: str


class ScheduleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    start_time: time
    end_time: time
    tolerance_minutes: int = Field(default=0, ge=0, le=240)


class ScheduleResponse(BaseModel):
    id: UUID
    name: str
    start_time: time
    end_time: time
    tolerance_minutes: int


class EmployeeSyncRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=False)

    display_name: str = Field(min_length=1, max_length=180)
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    site_id: UUID | None = None
    schedule_id: UUID | None = None
    attendance_eligible: bool = True


class EmployeeResponse(BaseModel):
    id: UUID
    external_employee_id: str
    display_name: str
    status: EmployeeStatus
    site_id: UUID | None
    schedule_id: UUID | None
    attendance_eligible: bool
