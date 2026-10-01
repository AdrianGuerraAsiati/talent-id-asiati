from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from talent_id.modules.attendance.application import AttendanceService
from talent_id.modules.attendance.repository import AttendanceRepository
from talent_id.modules.workforce.dependencies import WorkforceServiceDependency
from talent_id.shared.db import get_session

SessionDependency = Annotated[Session, Depends(get_session)]


def get_attendance_service(
    session: SessionDependency,
    workforce: WorkforceServiceDependency,
) -> AttendanceService:
    return AttendanceService(AttendanceRepository(session), workforce)


AttendanceServiceDependency = Annotated[AttendanceService, Depends(get_attendance_service)]
