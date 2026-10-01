from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status

from talent_id.modules.devices.application import (
    DeviceNotFoundError,
    InvalidDeviceCredentialsError,
    InvalidDeviceSiteError,
)
from talent_id.modules.devices.dependencies import DeviceServiceDependency
from talent_id.modules.devices.schemas import (
    DeviceProvisionRequest,
    DeviceProvisionResponse,
    DeviceResponse,
    KioskContextResponse,
)
from talent_id.modules.workforce.application import WorkforceNotFoundError
from talent_id.modules.workforce.dependencies import WorkforceServiceDependency
from talent_id.shared.auth import require_internal_key

router = APIRouter(
    prefix="/v1/devices",
    tags=["devices"],
    dependencies=[Depends(require_internal_key)],
)
kiosk_router = APIRouter(prefix="/v1/kiosk", tags=["kiosk"])

DeviceIdHeader = Annotated[UUID, Header(alias="X-Device-Id")]
DeviceSecretHeader = Annotated[str, Header(alias="X-Device-Secret")]


@router.post("", response_model=DeviceProvisionResponse, status_code=status.HTTP_201_CREATED)
def provision_device(
    payload: DeviceProvisionRequest,
    devices: DeviceServiceDependency,
) -> DeviceProvisionResponse:
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
    devices: DeviceServiceDependency,
) -> DeviceResponse:
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
    x_device_id: DeviceIdHeader,
    x_device_secret: DeviceSecretHeader,
    devices: DeviceServiceDependency,
    workforce: WorkforceServiceDependency,
) -> KioskContextResponse:
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
