from datetime import UTC, datetime
from uuid import UUID

from talent_id.modules.biometrics.domain import (
    BiometricEnrollment,
    RecognizedEmployee,
)
from talent_id.modules.biometrics.ports import BiometricProvider
from talent_id.modules.biometrics.repository import BiometricEnrollmentRepository
from talent_id.modules.workforce.application import (
    WorkforceNotFoundError,
    WorkforceService,
)
from talent_id.modules.workforce.domain import EmployeeStatus


class BiometricEnrollmentNotFoundError(LookupError):
    pass


class BiometricEmployeeNotAllowedError(PermissionError):
    pass


class BiometricService:
    def __init__(
        self,
        *,
        provider: BiometricProvider,
        repository: BiometricEnrollmentRepository,
        workforce: WorkforceService,
        match_threshold: float,
    ) -> None:
        self._provider = provider
        self._repository = repository
        self._workforce = workforce
        self._match_threshold = match_threshold

    def enroll(self, *, employee_id: UUID, image_bytes: bytes) -> BiometricEnrollment:
        employee = self._get_allowed_employee(employee_id)
        provider_user_id = str(employee.employee_id)

        result = self._provider.enroll(
            provider_user_id=provider_user_id,
            image_bytes=image_bytes,
        )

        existing = self._repository.get_by_employee(employee.employee_id)
        enrollment = BiometricEnrollment(
            employee_id=employee.employee_id,
            provider=self._provider.provider_name,
            provider_user_id=result.provider_user_id,
            face_count=(existing.face_count if existing else 0) + len(result.face_ids),
            active=True,
            enrolled_at=existing.enrolled_at if existing else datetime.now(UTC),
        )
        return self._repository.upsert(enrollment)

    def recognize(self, *, image_bytes: bytes) -> RecognizedEmployee | None:
        match = self._provider.recognize(
            image_bytes=image_bytes,
            threshold=self._match_threshold,
        )
        if match is None:
            return None

        enrollment = self._repository.get_by_provider_user_id(match.provider_user_id)
        if enrollment is None or not enrollment.active:
            return None

        try:
            employee = self._get_allowed_employee(enrollment.employee_id)
        except BiometricEmployeeNotAllowedError:
            return None

        return RecognizedEmployee(
            employee_id=employee.employee_id,
            display_name=employee.display_name,
            similarity=match.similarity,
        )

    def _get_allowed_employee(self, employee_id: UUID):
        try:
            employee = self._workforce.get_employee_by_id(employee_id)
        except WorkforceNotFoundError as exc:
            raise BiometricEmployeeNotAllowedError("employee not found") from exc

        if employee.status is not EmployeeStatus.ACTIVE:
            raise BiometricEmployeeNotAllowedError("employee is inactive")
        if not employee.attendance_eligible:
            raise BiometricEmployeeNotAllowedError(
                "employee is not eligible for biometric attendance"
            )
        return employee
