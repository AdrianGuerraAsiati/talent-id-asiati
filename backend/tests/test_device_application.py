from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from talent_id.modules.devices.application import (
    DeviceProvisioningService,
    InvalidDeviceCredentialsError,
)
from talent_id.modules.devices.domain import KioskDevice


class FakeDeviceRepository:
    def __init__(self) -> None:
        self.items: dict[UUID, KioskDevice] = {}

    def create(self, device: KioskDevice) -> KioskDevice:
        self.items[device.device_id] = device
        return device

    def get(self, device_id: UUID) -> KioskDevice | None:
        return self.items.get(device_id)

    def set_active(self, device_id: UUID, active: bool) -> KioskDevice | None:
        current = self.items.get(device_id)
        if current is None:
            return None
        updated = KioskDevice(
            device_id=current.device_id,
            site_id=current.site_id,
            name=current.name,
            token_hash=current.token_hash,
            active=active,
            last_seen_at=current.last_seen_at,
        )
        self.items[device_id] = updated
        return updated

    def touch(self, device_id: UUID, last_seen_at: datetime) -> KioskDevice | None:
        current = self.items.get(device_id)
        if current is None:
            return None
        updated = KioskDevice(
            device_id=current.device_id,
            site_id=current.site_id,
            name=current.name,
            token_hash=current.token_hash,
            active=current.active,
            last_seen_at=last_seen_at,
        )
        self.items[device_id] = updated
        return updated


class FakeWorkforce:
    def __init__(self, site_id: UUID) -> None:
        self.site_id = site_id

    def site_exists(self, site_id: UUID) -> bool:
        return site_id == self.site_id


def test_device_can_be_provisioned_authenticated_and_revoked() -> None:
    site_id = uuid4()
    repository = FakeDeviceRepository()
    service = DeviceProvisioningService(repository, FakeWorkforce(site_id))  # type: ignore[arg-type]

    device, secret = service.provision(site_id=site_id, name="Recepcion Bogota")

    authenticated = service.authenticate(device_id=device.device_id, secret=secret)
    assert authenticated.active
    assert authenticated.last_seen_at is not None
    assert authenticated.last_seen_at <= datetime.now(UTC)

    service.revoke(device.device_id)

    with pytest.raises(InvalidDeviceCredentialsError):
        service.authenticate(device_id=device.device_id, secret=secret)
