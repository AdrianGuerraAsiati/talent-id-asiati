from datetime import UTC, datetime
from uuid import uuid4

import pytest

from talent_id.modules.rewards.domain import PointTransaction, PointTransactionType


def test_point_transaction_cannot_be_zero() -> None:
    with pytest.raises(ValueError, match="cannot be zero"):
        PointTransaction(
            employee_id=uuid4(),
            amount=0,
            transaction_type=PointTransactionType.ADJUSTMENT,
            reason="test",
            occurred_at=datetime.now(UTC),
        )


def test_point_transaction_requires_reason() -> None:
    with pytest.raises(ValueError, match="reason"):
        PointTransaction(
            employee_id=uuid4(),
            amount=10,
            transaction_type=PointTransactionType.EARN,
            reason=" ",
            occurred_at=datetime.now(UTC),
        )
