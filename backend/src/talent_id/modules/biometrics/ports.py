from typing import Protocol

from talent_id.modules.biometrics.domain import EnrollmentResult, RecognitionMatch


class BiometricProvider(Protocol):
    provider_name: str

    def enroll(self, *, provider_user_id: str, image_bytes: bytes) -> EnrollmentResult:
        ...

    def recognize(
        self,
        *,
        image_bytes: bytes,
        threshold: float,
    ) -> RecognitionMatch | None:
        ...
