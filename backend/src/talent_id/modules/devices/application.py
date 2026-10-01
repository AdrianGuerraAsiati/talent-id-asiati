from datetime import UTC, datetime
from uuid import UUID

from talent_id.modules.devices.domain import KioskDevice
from talent_id.modules.devices.repository import DeviceRepository
from talent_id.modules.devices.security import (
    hash_device_secret,
    issue_device_secret,
    verify_device_secret,
)
from talent_id.modules.workforce.application import WorkforceService


class DeviceNotFoundError(LookupError):
    pass


class InvalidDeviceCredentialsError(PermissionError):
    pass


class InvalidDeviceSiteError(ValueError):
    pass


class DeviceProvisioningService:
    def __init__(
        self,
        repository: DeviceRepository,
        workforce: WorkforceService,
    ) -> None:
        self._repository = repository
        self._workforce = workforce

    def provision(self, *, site_id: UUID, name: str) -> tuple[KioskDevice, str]:
        if not self._workforce.site_exists(site_id):
            raise InvalidDeviceSiteError("site not found")

        secret = issue_device_secret()
        device = KioskDevice(
            site_id=site_id,
            name=name,
            token_hash=hash_device_secret(secret),
        )
        return self._repository.create(device), secret

    def authenticate(self, *, device_id: UUID, secret: str) -> KioskDevice:
        device = self._repository.get(device_id)
        if device is None:
            raise DeviceNotFoundError("device not found")
        if not device.active or not verify_device_secret(secret, device.token_hash):
            raise InvalidDeviceCredentialsError("invalid device credentials")

        touched = self._repository.touch(device_id, datetime.now(UTC))
        if touched is None:
            raise DeviceNotFoundError("device not found")
        return touched

    def revoke(self, device_id: UUID) -> KioskDevice:
        device = self._repository.set_active(device_id, False)
        if device is None:
            raise DeviceNotFoundError("device not found")
        return device
