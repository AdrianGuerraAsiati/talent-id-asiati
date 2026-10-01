from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RecognitionMatch:
    provider_user_id: str
    similarity: float

    def __post_init__(self) -> None:
        if not 0 <= self.similarity <= 100:
            raise ValueError("similarity must be between 0 and 100")


@dataclass(frozen=True, slots=True)
class EnrollmentResult:
    provider_user_id: str
    face_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.face_ids:
            raise ValueError("enrollment must contain at least one face")


@dataclass(frozen=True, slots=True)
class BiometricEnrollment:
    employee_id: UUID
    provider: str
    provider_user_id: str
    face_count: int
    active: bool
    enrolled_at: datetime

    def __post_init__(self) -> None:
        if self.face_count < 1:
            raise ValueError("face_count must be at least one")
        if self.enrolled_at.tzinfo is None:
            raise ValueError("enrolled_at must be timezone-aware")


@dataclass(frozen=True, slots=True)
class RecognizedEmployee:
    employee_id: UUID
    display_name: str
    similarity: float
