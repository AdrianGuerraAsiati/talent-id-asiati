from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4


class PointTransactionType(StrEnum):
    EARN = "earn"
    SPEND = "spend"
    ADJUSTMENT = "adjustment"


@dataclass(frozen=True, slots=True)
class PointTransaction:
    employee_id: UUID
    amount: int
    transaction_type: PointTransactionType
    reason: str
    occurred_at: datetime
    source_event_id: UUID | None = None
    transaction_id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if self.amount == 0:
            raise ValueError("point transaction amount cannot be zero")
        if not self.reason.strip():
            raise ValueError("point transaction reason is required")
