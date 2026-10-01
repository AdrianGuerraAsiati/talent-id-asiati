from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TypeVar
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class DomainEvent:
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


EventT = TypeVar("EventT", bound=DomainEvent)
Handler = Callable[[DomainEvent], None]


class InMemoryEventBus:
    """Synchronous process-local event bus for module decoupling during bootstrap."""

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[Handler]] = defaultdict(list)

    def subscribe(self, event_type: type[EventT], handler: Callable[[EventT], None]) -> None:
        self._handlers[event_type].append(handler)  # type: ignore[arg-type]

    def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers[type(event)]:
            handler(event)
