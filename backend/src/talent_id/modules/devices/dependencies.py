from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from talent_id.modules.devices.application import DeviceProvisioningService
from talent_id.modules.devices.repository import DeviceRepository
from talent_id.modules.workforce.dependencies import WorkforceServiceDependency
from talent_id.shared.db import get_session

SessionDependency = Annotated[Session, Depends(get_session)]


def get_device_service(
    session: SessionDependency,
    workforce: WorkforceServiceDependency,
) -> DeviceProvisioningService:
    return DeviceProvisioningService(DeviceRepository(session), workforce)


DeviceServiceDependency = Annotated[DeviceProvisioningService, Depends(get_device_service)]
