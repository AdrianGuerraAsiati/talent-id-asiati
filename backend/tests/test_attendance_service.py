from datetime import UTC, datetime
from uuid import UUID, uuid4

from talent_id.modules.attendance.application import AttendanceService
from talent_id.modules.attendance.domain import (
    AttendanceEvent,
    AttendanceEventType,
    AttendanceMethod,
)
from talent_id.modules.workforce.domain import EmployeeProjection, EmployeeStatus


class FakeAttendanceRepository:
    def __init__(self) -> None:
        self.by_key: dict[str, AttendanceEvent] = {}

    def get_by_idempotency_key(self, key: str) -> AttendanceEvent | None:
        return self.by_key.get(key)

    def append(self, event: AttendanceEvent) -> AttendanceEvent:
        self.by_key[event.idempotency_key] = event
        return event

    def get_last_for_employee(self, employee_id: UUID) -> AttendanceEvent | None:
        events = [event for event in self.by_key.values() if event.employee_id == employee_id]
        return events[-1] if events else None


class FakeWorkforce:
    def __init__(self, employee: EmployeeProjection) -> None:
        self.employee = employee

    def get_employee_by_id(self, employee_id: UUID) -> EmployeeProjection:
        assert employee_id == self.employee.employee_id
        return self.employee


def test_attendance_retries_return_existing_event() -> None:
    employee = EmployeeProjection(
        external_employee_id="talent-001",
        display_name="Employee",
        status=EmployeeStatus.ACTIVE,
    )
    repository = FakeAttendanceRepository()
    service = AttendanceService(repository, FakeWorkforce(employee))  # type: ignore[arg-type]

    args = {
        "employee_id": employee.employee_id,
        "site_id": uuid4(),
        "device_id": uuid4(),
        "event_type": AttendanceEventType.CHECK_IN,
        "method": AttendanceMethod.FACE,
        "idempotency_key": "device:request-001",
        "recognition_confidence": 99.3,
        "occurred_at": datetime.now(UTC),
    }

    first, first_created = service.record(**args)
    second, second_created = service.record(**args)

    assert first_created is True
    assert second_created is False
    assert first.event_id == second.event_id
    assert len(repository.by_key) == 1
