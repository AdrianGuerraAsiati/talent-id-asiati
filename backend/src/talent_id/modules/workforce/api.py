from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from talent_id.modules.workforce.application import (
    WorkforceNotFoundError,
    WorkforceService,
)
from talent_id.modules.workforce.repository import WorkforceRepository
from talent_id.modules.workforce.schemas import (
    EmployeeResponse,
    EmployeeSyncRequest,
    ScheduleCreate,
    ScheduleResponse,
    SiteCreate,
    SiteResponse,
)
from talent_id.shared.auth import require_internal_key
from talent_id.shared.db import get_session

router = APIRouter(
    prefix="/v1/workforce",
    tags=["workforce"],
    dependencies=[Depends(require_internal_key)],
)

SessionDependency = Annotated[Session, Depends(get_session)]


def get_service(session: SessionDependency) -> WorkforceService:
    return WorkforceService(WorkforceRepository(session))


WorkforceServiceDependency = Annotated[WorkforceService, Depends(get_service)]


@router.post("/sites", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
def create_site(payload: SiteCreate, service: WorkforceServiceDependency) -> SiteResponse:
    try:
        site = service.create_site(name=payload.name, timezone=payload.timezone, code=payload.code)
        return SiteResponse(id=site.site_id, name=site.name, code=site.code, timezone=site.timezone)
    except (ValueError, IntegrityError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/schedules", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_schedule(
    payload: ScheduleCreate,
    service: WorkforceServiceDependency,
) -> ScheduleResponse:
    try:
        schedule = service.create_schedule(
            name=payload.name,
            start_time=payload.start_time,
            end_time=payload.end_time,
            tolerance_minutes=payload.tolerance_minutes,
        )
        return ScheduleResponse(
            id=schedule.schedule_id,
            name=schedule.name,
            start_time=schedule.start_time,
            end_time=schedule.end_time,
            tolerance_minutes=schedule.tolerance_minutes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.put("/employees/{external_employee_id}", response_model=EmployeeResponse)
def sync_employee(
    external_employee_id: str,
    payload: EmployeeSyncRequest,
    service: WorkforceServiceDependency,
) -> EmployeeResponse:
    try:
        employee = service.upsert_employee(
            external_employee_id=external_employee_id,
            display_name=payload.display_name,
            status=payload.status,
            site_id=payload.site_id,
            schedule_id=payload.schedule_id,
            attendance_eligible=payload.attendance_eligible,
        )
    except WorkforceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return EmployeeResponse(
        id=employee.employee_id,
        external_employee_id=employee.external_employee_id,
        display_name=employee.display_name,
        status=employee.status,
        site_id=employee.site_id,
        schedule_id=employee.schedule_id,
        attendance_eligible=employee.attendance_eligible,
    )


@router.get("/employees/{external_employee_id}", response_model=EmployeeResponse)
def get_employee(
    external_employee_id: str,
    service: WorkforceServiceDependency,
) -> EmployeeResponse:
    try:
        employee = service.get_employee(external_employee_id)
    except WorkforceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return EmployeeResponse(
        id=employee.employee_id,
        external_employee_id=employee.external_employee_id,
        display_name=employee.display_name,
        status=employee.status,
        site_id=employee.site_id,
        schedule_id=employee.schedule_id,
        attendance_eligible=employee.attendance_eligible,
    )
