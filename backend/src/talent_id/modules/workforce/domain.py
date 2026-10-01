from dataclasses import dataclass, field
from datetime import time
from enum import StrEnum
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class EmployeeStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


@dataclass(frozen=True, slots=True)
class Site:
    name: str
    timezone: str
    site_id: UUID = field(default_factory=uuid4)
    code: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("site name is required")
        try:
            ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("invalid site timezone") from exc


@dataclass(frozen=True, slots=True)
class WorkSchedule:
    name: str
    start_time: time
    end_time: time
    tolerance_minutes: int = 0
    schedule_id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("schedule name is required")
        if self.tolerance_minutes < 0:
            raise ValueError("tolerance_minutes cannot be negative")
        if self.start_time == self.end_time:
            raise ValueError("schedule start and end cannot be equal")


@dataclass(frozen=True, slots=True)
class EmployeeProjection:
    external_employee_id: str
    display_name: str
    status: EmployeeStatus
    site_id: UUID | None = None
    schedule_id: UUID | None = None
    attendance_eligible: bool = True
    employee_id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.external_employee_id.strip():
            raise ValueError("external_employee_id is required")
        if not self.display_name.strip():
            raise ValueError("display_name is required")
