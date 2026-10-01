from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DeviceProvisionRequest(BaseModel):
    site_id: UUID
    name: str = Field(min_length=1, max_length=120)


class DeviceProvisionResponse(BaseModel):
    id: UUID
    site_id: UUID
    name: str
    active: bool
    device_secret: str


class DeviceResponse(BaseModel):
    id: UUID
    site_id: UUID
    name: str
    active: bool
    last_seen_at: datetime | None


class KioskContextResponse(BaseModel):
    device: DeviceResponse
    site_name: str
    site_timezone: str
