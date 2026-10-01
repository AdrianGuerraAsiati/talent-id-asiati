from datetime import time
from uuid import UUID, uuid4

from sqlalchemy import Boolean, ForeignKey, String, Time, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from talent_id.shared.db import Base


class SiteModel(Base):
    __tablename__ = "workforce_sites"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    code: Mapped[str | None] = mapped_column(String(32), nullable=True, unique=True)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False)


class WorkScheduleModel(Base):
    __tablename__ = "workforce_schedules"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    start_time: Mapped[time] = mapped_column(Time(), nullable=False)
    end_time: Mapped[time] = mapped_column(Time(), nullable=False)
    tolerance_minutes: Mapped[int] = mapped_column(nullable=False, default=0)


class EmployeeProjectionModel(Base):
    __tablename__ = "workforce_employees"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    external_employee_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(180), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    site_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workforce_sites.id", ondelete="SET NULL"),
        nullable=True,
    )
    schedule_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workforce_schedules.id", ondelete="SET NULL"),
        nullable=True,
    )
    attendance_eligible: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
