from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class KioskDevice:
    site_id: UUID
    name: str
    token_hash: str
    active: bool = True
    last_seen_at: datetime | None = None
    device_id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("device name is required")
        if not self.token_hash.strip():
            raise ValueError("device token hash is required")
