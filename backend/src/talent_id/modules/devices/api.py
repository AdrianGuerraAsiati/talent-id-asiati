from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from talent_id.modules.devices.application import (
    DeviceNotFoundError,
    DeviceProvisioningService,
    InvalidDeviceCredentialsError,
    InvalidDeviceSiteError,
)
from talent_id.modules.devices.repository import DeviceRepository
from talent_id.modules.devices.schemas import (
    DeviceProvisionRequest,
    DeviceProvisionResponse,
    DeviceResponse,
    KioskContextResponse,
)
from talent_id.modules.workforce.application import (
    WorkforceNotFoundError,
    WorkforceService,
)
from talent_id.modules.workforce.repository import WorkforceRepository
from talent_id.shared.db import get_session

router = APIRouter(prefix="/v1/devices", tags=["devices"])
kiosk_router = APIRouter(prefix="/v1/kiosk", tags=["kiosk"])


def build_services(
    session: Session,
) -> tuple[DeviceProvisioningService, WorkforceService]:
    workforce = WorkforceService(WorkforceRepository(session))
    devices = DeviceProvisioningService(DeviceRepository(session), workforce)
    return devices, workforce


@router.post("", response_model=DeviceProvisionResponse, status_code=status.HTTP_201_CREATED)
def provision_device(
    payload: DeviceProvisionRequest,
    session: Session = Depends(get_session),
) -> DeviceProvisionResponse:
    devices, _ = build_services(session)
    try:
        device, secret = devices.provision(site_id=payload.site_id, name=payload.name)
    except InvalidDeviceSiteError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return DeviceProvisionResponse(
        id=device.device_id,
        site_id=device.site_id,
        name=device.name,
        active=device.active,
        device_secret=secret,
    )


@router.post("/{device_id}/revoke", response_model=DeviceResponse)
def revoke_device(
    device_id: UUID,
    session: Session = Depends(get_session),
) -> DeviceResponse:
    devices, _ = build_services(session)
    try:
        device = devices.revoke(device_id)
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return DeviceResponse(
        id=device.device_id,
        site_id=device.site_id,
        name=device.name,
        active=device.active,
        last_seen_at=device.last_seen_at,
    )


@kiosk_router.get("/context", response_model=KioskContextResponse)
def kiosk_context(
    x_device_id: UUID = Header(alias="X-Device-Id"),
    x_device_secret: str = Header(alias="X-Device-Secret"),
    session: Session = Depends(get_session),
) -> KioskContextResponse:
    devices, workforce = build_services(session)

    try:
        device = devices.authenticate(device_id=x_device_id, secret=x_device_secret)
        site = workforce.get_site(device.site_id)
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail="device not found") from exc
    except InvalidDeviceCredentialsError as exc:
        raise HTTPException(status_code=401, detail="invalid device credentials") from exc
    except WorkforceNotFoundError as exc:
        raise HTTPException(status_code=409, detail="device site is no longer available") from exc

    return KioskContextResponse(
        device=DeviceResponse(
            id=device.device_id,
            site_id=device.site_id,
            name=device.name,
            active=device.active,
            last_seen_at=device.last_seen_at,
        ),
        site_name=site.name,
        site_timezone=site.timezone,
    )
