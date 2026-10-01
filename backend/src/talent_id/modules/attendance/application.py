from datetime import UTC, datetime
from uuid import UUID

from talent_id.modules.attendance.domain import (
    AttendanceEvent,
    AttendanceEventType,
    AttendanceMethod,
)
from talent_id.modules.attendance.repository import AttendanceRepository
from talent_id.modules.workforce.application import (
    WorkforceNotFoundError,
    WorkforceService,
)
from talent_id.modules.workforce.domain import EmployeeStatus


class AttendanceNotAllowedError(PermissionError):
    pass


class AttendanceService:
    def __init__(
        self,
        repository: AttendanceRepository,
        workforce: WorkforceService,
    ) -> None:
        self._repository = repository
        self._workforce = workforce

    def record(
        self,
        *,
        employee_id: UUID,
        site_id: UUID,
        device_id: UUID | None,
        event_type: AttendanceEventType,
        method: AttendanceMethod,
        idempotency_key: str,
        recognition_confidence: float | None = None,
        occurred_at: datetime | None = None,
    ) -> tuple[AttendanceEvent, bool]:
        existing = self._repository.get_by_idempotency_key(idempotency_key)
        if existing is not None:
            return existing, False

        try:
            employee = self._workforce.get_employee_by_id(employee_id)
        except WorkforceNotFoundError as exc:
            raise AttendanceNotAllowedError("employee not found") from exc

        if employee.status is not EmployeeStatus.ACTIVE:
            raise AttendanceNotAllowedError("employee is inactive")
        if not employee.attendance_eligible:
            raise AttendanceNotAllowedError("employee is not eligible for attendance")

        event = AttendanceEvent(
            employee_id=employee.employee_id,
            site_id=site_id,
            device_id=device_id,
            event_type=event_type,
            method=method,
            occurred_at=occurred_at or datetime.now(UTC),
            idempotency_key=idempotency_key,
            recognition_confidence=recognition_confidence,
        )
        return self._repository.append(event), True

    def get_last_event(self, employee_id: UUID) -> AttendanceEvent | None:
        return self._repository.get_last_for_employee(employee_id)
