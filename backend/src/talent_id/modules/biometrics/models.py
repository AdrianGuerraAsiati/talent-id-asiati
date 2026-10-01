from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from talent_id.shared.db import Base


class BiometricEnrollmentModel(Base):
    __tablename__ = "biometrics_enrollments"

    employee_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    provider_user_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    face_count: Mapped[int] = mapped_column(Integer(), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
