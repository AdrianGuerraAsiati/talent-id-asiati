"""Create attendance and biometric enrollment tables.

Revision ID: 20261001_0002
Revises: 20261001_0001
Create Date: 2026-10-01
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261001_0002"
down_revision: str | Sequence[str] | None = "20261001_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "biometrics_enrollments",
        sa.Column("employee_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("provider_user_id", sa.String(length=128), nullable=False),
        sa.Column("face_count", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("employee_id"),
        sa.UniqueConstraint("provider_user_id"),
    )

    op.create_table(
        "attendance_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("employee_id", sa.Uuid(), nullable=False),
        sa.Column("site_id", sa.Uuid(), nullable=False),
        sa.Column("device_id", sa.Uuid(), nullable=True),
        sa.Column("event_type", sa.String(length=24), nullable=False),
        sa.Column("method", sa.String(length=24), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("recognition_confidence", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
    )
    op.create_index(
        op.f("ix_attendance_events_device_id"),
        "attendance_events",
        ["device_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_attendance_events_employee_id"),
        "attendance_events",
        ["employee_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_attendance_events_occurred_at"),
        "attendance_events",
        ["occurred_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_attendance_events_site_id"),
        "attendance_events",
        ["site_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_attendance_events_site_id"), table_name="attendance_events")
    op.drop_index(op.f("ix_attendance_events_occurred_at"), table_name="attendance_events")
    op.drop_index(op.f("ix_attendance_events_employee_id"), table_name="attendance_events")
    op.drop_index(op.f("ix_attendance_events_device_id"), table_name="attendance_events")
    op.drop_table("attendance_events")
    op.drop_table("biometrics_enrollments")
