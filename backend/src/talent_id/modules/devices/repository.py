from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from talent_id.modules.devices.domain import KioskDevice
from talent_id.modules.devices.models import KioskDeviceModel


class DeviceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, device: KioskDevice) -> KioskDevice:
        model = KioskDeviceModel(
            id=device.device_id,
            site_id=device.site_id,
            name=device.name,
            token_hash=device.token_hash,
            active=device.active,
            last_seen_at=device.last_seen_at,
        )
        self._session.add(model)
        self._session.flush()
        return device

    def get(self, device_id: UUID) -> KioskDevice | None:
        model = self._session.get(KioskDeviceModel, device_id)
        if model is None:
            return None
        return self._to_domain(model)

    def set_active(self, device_id: UUID, active: bool) -> KioskDevice | None:
        model = self._session.get(KioskDeviceModel, device_id)
        if model is None:
            return None
        model.active = active
        self._session.flush()
        return self._to_domain(model)

    def touch(self, device_id: UUID, last_seen_at: datetime) -> KioskDevice | None:
        model = self._session.get(KioskDeviceModel, device_id)
        if model is None:
            return None
        model.last_seen_at = last_seen_at
        self._session.flush()
        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: KioskDeviceModel) -> KioskDevice:
        return KioskDevice(
            device_id=model.id,
            site_id=model.site_id,
            name=model.name,
            token_hash=model.token_hash,
            active=model.active,
            last_seen_at=model.last_seen_at,
        )
