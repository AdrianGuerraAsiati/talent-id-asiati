from datetime import UTC, datetime
from uuid import uuid4

import pytest

from talent_id.modules.attendance.domain import (
    AttendanceEvent,
    AttendanceEventType,
    AttendanceMethod,
)


def test_attendance_confidence_must_be_valid_percentage() -> None:
    with pytest.raises(ValueError, match="recognition_confidence"):
        AttendanceEvent(
            employee_id=uuid4(),
            site_id=uuid4(),
            device_id=uuid4(),
            event_type=AttendanceEventType.CHECK_IN,
            method=AttendanceMethod.FACE,
            occurred_at=datetime.now(UTC),
            idempotency_key="device:event",
            recognition_confidence=101,
        )


def test_attendance_requires_idempotency_key() -> None:
    with pytest.raises(ValueError, match="idempotency_key"):
        AttendanceEvent(
            employee_id=uuid4(),
            site_id=uuid4(),
            device_id=None,
            event_type=AttendanceEventType.CHECK_IN,
            method=AttendanceMethod.PIN,
            occurred_at=datetime.now(UTC),
            idempotency_key=" ",
        )
