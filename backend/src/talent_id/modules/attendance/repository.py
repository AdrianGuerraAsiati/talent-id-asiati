from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from talent_id.modules.attendance.domain import (
    AttendanceEvent,
    AttendanceEventType,
    AttendanceMethod,
)
from talent_id.modules.attendance.models import AttendanceEventModel


class AttendanceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def append(self, event: AttendanceEvent) -> AttendanceEvent:
        model = AttendanceEventModel(
            id=event.event_id,
            employee_id=event.employee_id,
            site_id=event.site_id,
            device_id=event.device_id,
            event_type=event.event_type.value,
            method=event.method.value,
            occurred_at=event.occurred_at,
            idempotency_key=event.idempotency_key,
            recognition_confidence=event.recognition_confidence,
        )
        self._session.add(model)
        self._session.flush()
        return event

    def get_by_idempotency_key(self, idempotency_key: str) -> AttendanceEvent | None:
        model = self._session.scalar(
            select(AttendanceEventModel).where(
                AttendanceEventModel.idempotency_key == idempotency_key
            )
        )
        return self._to_domain(model) if model is not None else None

    def get_last_for_employee(self, employee_id: UUID) -> AttendanceEvent | None:
        model = self._session.scalar(
            select(AttendanceEventModel)
            .where(AttendanceEventModel.employee_id == employee_id)
            .order_by(
                AttendanceEventModel.occurred_at.desc(),
                AttendanceEventModel.id.desc(),
            )
            .limit(1)
        )
        return self._to_domain(model) if model is not None else None

    @staticmethod
    def _to_domain(model: AttendanceEventModel) -> AttendanceEvent:
        return AttendanceEvent(
            event_id=model.id,
            employee_id=model.employee_id,
            site_id=model.site_id,
            device_id=model.device_id,
            event_type=AttendanceEventType(model.event_type),
            method=AttendanceMethod(model.method),
            occurred_at=model.occurred_at,
            idempotency_key=model.idempotency_key,
            recognition_confidence=model.recognition_confidence,
        )
