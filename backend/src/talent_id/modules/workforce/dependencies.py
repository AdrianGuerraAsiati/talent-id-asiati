from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from talent_id.modules.workforce.application import WorkforceService
from talent_id.modules.workforce.repository import WorkforceRepository
from talent_id.shared.db import get_session

SessionDependency = Annotated[Session, Depends(get_session)]


def get_workforce_service(session: SessionDependency) -> WorkforceService:
    return WorkforceService(WorkforceRepository(session))


WorkforceServiceDependency = Annotated[WorkforceService, Depends(get_workforce_service)]
