from datetime import time
from uuid import UUID

from talent_id.modules.workforce.domain import (
    EmployeeProjection,
    EmployeeStatus,
    Site,
    WorkSchedule,
)
from talent_id.modules.workforce.repository import WorkforceRepository


class WorkforceNotFoundError(LookupError):
    pass


class WorkforceService:
    def __init__(self, repository: WorkforceRepository) -> None:
        self._repository = repository

    def create_site(self, *, name: str, timezone: str, code: str | None = None) -> Site:
        return self._repository.create_site(Site(name=name, timezone=timezone, code=code))

    def get_site(self, site_id: UUID) -> Site:
        site = self._repository.get_site(site_id)
        if site is None:
            raise WorkforceNotFoundError("site not found")
        return site

    def site_exists(self, site_id: UUID) -> bool:
        return self._repository.get_site(site_id) is not None

    def create_schedule(
        self,
        *,
        name: str,
        start_time: time,
        end_time: time,
        tolerance_minutes: int,
    ) -> WorkSchedule:
        return self._repository.create_schedule(
            WorkSchedule(
                name=name,
                start_time=start_time,
                end_time=end_time,
                tolerance_minutes=tolerance_minutes,
            )
        )

    def upsert_employee(
        self,
        *,
        external_employee_id: str,
        display_name: str,
        status: EmployeeStatus,
        site_id: UUID | None,
        schedule_id: UUID | None,
        attendance_eligible: bool,
    ) -> EmployeeProjection:
        if site_id is not None and not self.site_exists(site_id):
            raise WorkforceNotFoundError("site not found")
        if schedule_id is not None and self._repository.get_schedule(schedule_id) is None:
            raise WorkforceNotFoundError("schedule not found")

        existing = self._repository.get_employee_by_external_id(external_employee_id)
        common = {
            "external_employee_id": external_employee_id,
            "display_name": display_name,
            "status": status,
            "site_id": site_id,
            "schedule_id": schedule_id,
            "attendance_eligible": attendance_eligible,
        }
        employee = (
            EmployeeProjection(employee_id=existing.employee_id, **common)
            if existing is not None
            else EmployeeProjection(**common)
        )
        return self._repository.upsert_employee(employee)

    def get_employee(self, external_employee_id: str) -> EmployeeProjection:
        employee = self._repository.get_employee_by_external_id(external_employee_id)
        if employee is None:
            raise WorkforceNotFoundError("employee not found")
        return employee
