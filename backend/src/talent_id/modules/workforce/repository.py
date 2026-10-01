from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from talent_id.modules.workforce.domain import (
    EmployeeProjection,
    EmployeeStatus,
    Site,
    WorkSchedule,
)
from talent_id.modules.workforce.models import (
    EmployeeProjectionModel,
    SiteModel,
    WorkScheduleModel,
)


class WorkforceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_site(self, site: Site) -> Site:
        model = SiteModel(
            id=site.site_id,
            name=site.name,
            code=site.code,
            timezone=site.timezone,
        )
        self._session.add(model)
        self._session.flush()
        return site

    def get_site(self, site_id: UUID) -> Site | None:
        model = self._session.get(SiteModel, site_id)
        if model is None:
            return None
        return Site(
            site_id=model.id,
            name=model.name,
            code=model.code,
            timezone=model.timezone,
        )

    def create_schedule(self, schedule: WorkSchedule) -> WorkSchedule:
        model = WorkScheduleModel(
            id=schedule.schedule_id,
            name=schedule.name,
            start_time=schedule.start_time,
            end_time=schedule.end_time,
            tolerance_minutes=schedule.tolerance_minutes,
        )
        self._session.add(model)
        self._session.flush()
        return schedule

    def get_schedule(self, schedule_id: UUID) -> WorkSchedule | None:
        model = self._session.get(WorkScheduleModel, schedule_id)
        if model is None:
            return None
        return WorkSchedule(
            schedule_id=model.id,
            name=model.name,
            start_time=model.start_time,
            end_time=model.end_time,
            tolerance_minutes=model.tolerance_minutes,
        )

    def upsert_employee(self, employee: EmployeeProjection) -> EmployeeProjection:
        model = self._session.scalar(
            select(EmployeeProjectionModel).where(
                EmployeeProjectionModel.external_employee_id == employee.external_employee_id
            )
        )
        if model is None:
            model = EmployeeProjectionModel(
                id=employee.employee_id,
                external_employee_id=employee.external_employee_id,
            )
            self._session.add(model)

        model.display_name = employee.display_name
        model.status = employee.status.value
        model.site_id = employee.site_id
        model.schedule_id = employee.schedule_id
        model.attendance_eligible = employee.attendance_eligible
        self._session.flush()

        return EmployeeProjection(
            employee_id=model.id,
            external_employee_id=model.external_employee_id,
            display_name=model.display_name,
            status=EmployeeStatus(model.status),
            site_id=model.site_id,
            schedule_id=model.schedule_id,
            attendance_eligible=model.attendance_eligible,
        )

    def get_employee_by_external_id(self, external_employee_id: str) -> EmployeeProjection | None:
        model = self._session.scalar(
            select(EmployeeProjectionModel).where(
                EmployeeProjectionModel.external_employee_id == external_employee_id
            )
        )
        if model is None:
            return None
        return EmployeeProjection(
            employee_id=model.id,
            external_employee_id=model.external_employee_id,
            display_name=model.display_name,
            status=EmployeeStatus(model.status),
            site_id=model.site_id,
            schedule_id=model.schedule_id,
            attendance_eligible=model.attendance_eligible,
        )
