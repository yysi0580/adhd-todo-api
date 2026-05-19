"""add calendar events

Revision ID: 20260519_0010
Revises: 20260506_0009
Create Date: 2026-05-19
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260519_0010"
down_revision: str | None = "20260506_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "calendar_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=True),
        sa.Column("action_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("timezone", sa.String(length=80), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("source", sa.String(length=40), nullable=False),
        sa.Column("external_uid", sa.String(length=255), nullable=True),
        sa.Column("provider", sa.String(length=60), nullable=True),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["action_id"], ["actions.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_uid"),
    )
    op.create_index(op.f("ix_calendar_events_id"), "calendar_events", ["id"], unique=False)
    op.create_index(
        op.f("ix_calendar_events_user_id"),
        "calendar_events",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_calendar_events_session_id"),
        "calendar_events",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_calendar_events_action_id"),
        "calendar_events",
        ["action_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_calendar_events_start_at"),
        "calendar_events",
        ["start_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_calendar_events_end_at"),
        "calendar_events",
        ["end_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_calendar_events_end_at"), table_name="calendar_events")
    op.drop_index(op.f("ix_calendar_events_start_at"), table_name="calendar_events")
    op.drop_index(op.f("ix_calendar_events_action_id"), table_name="calendar_events")
    op.drop_index(op.f("ix_calendar_events_session_id"), table_name="calendar_events")
    op.drop_index(op.f("ix_calendar_events_user_id"), table_name="calendar_events")
    op.drop_index(op.f("ix_calendar_events_id"), table_name="calendar_events")
    op.drop_table("calendar_events")
