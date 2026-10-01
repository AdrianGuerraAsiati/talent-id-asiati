from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from talent_id.modules.biometrics.domain import BiometricEnrollment
from talent_id.modules.biometrics.models import BiometricEnrollmentModel


class BiometricEnrollmentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert(self, enrollment: BiometricEnrollment) -> BiometricEnrollment:
        model = self._session.get(BiometricEnrollmentModel, enrollment.employee_id)
        if model is None:
            model = BiometricEnrollmentModel(employee_id=enrollment.employee_id)
            self._session.add(model)

        model.provider = enrollment.provider
        model.provider_user_id = enrollment.provider_user_id
        model.face_count = enrollment.face_count
        model.active = enrollment.active
        model.enrolled_at = enrollment.enrolled_at
        self._session.flush()
        return enrollment

    def get_by_employee(self, employee_id: UUID) -> BiometricEnrollment | None:
        model = self._session.get(BiometricEnrollmentModel, employee_id)
        return self._to_domain(model) if model is not None else None

    def get_by_provider_user_id(self, provider_user_id: str) -> BiometricEnrollment | None:
        model = self._session.scalar(
            select(BiometricEnrollmentModel).where(
                BiometricEnrollmentModel.provider_user_id == provider_user_id
            )
        )
        return self._to_domain(model) if model is not None else None

    @staticmethod
    def _to_domain(model: BiometricEnrollmentModel) -> BiometricEnrollment:
        return BiometricEnrollment(
            employee_id=model.employee_id,
            provider=model.provider,
            provider_user_id=model.provider_user_id,
            face_count=model.face_count,
            active=model.active,
            enrolled_at=model.enrolled_at,
        )
