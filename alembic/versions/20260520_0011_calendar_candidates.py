"""add calendar candidates

Revision ID: 20260520_0011
Revises: 20260519_0010
Create Date: 2026-05-20
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260520_0011"
down_revision: str | None = "20260519_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "calendar_candidates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("suggestion_id", sa.Integer(), nullable=True),
        sa.Column("action_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("micro_step", sa.Text(), nullable=False),
        sa.Column("candidate_type", sa.String(length=30), nullable=False),
        sa.Column("estimated_minutes", sa.Integer(), nullable=False),
        sa.Column("min_minutes", sa.Integer(), nullable=False),
        sa.Column("max_minutes", sa.Integer(), nullable=False),
        sa.Column("preferred_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("earliest_start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("latest_end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("preferred_time_block", sa.String(length=30), nullable=False),
        sa.Column("energy_level", sa.String(length=20), nullable=False),
        sa.Column("friction_level", sa.String(length=20), nullable=False),
        sa.Column("split_strategy", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("timezone", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["action_id"], ["actions.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"]),
        sa.ForeignKeyConstraint(["suggestion_id"], ["suggestions.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_calendar_candidates_id"),
        "calendar_candidates",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_calendar_candidates_user_id"),
        "calendar_candidates",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_calendar_candidates_session_id"),
        "calendar_candidates",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_calendar_candidates_suggestion_id"),
        "calendar_candidates",
        ["suggestion_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_calendar_candidates_action_id"),
        "calendar_candidates",
        ["action_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_calendar_candidates_status"),
        "calendar_candidates",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_calendar_candidates_status"), table_name="calendar_candidates")
    op.drop_index(op.f("ix_calendar_candidates_action_id"), table_name="calendar_candidates")
    op.drop_index(op.f("ix_calendar_candidates_suggestion_id"), table_name="calendar_candidates")
    op.drop_index(op.f("ix_calendar_candidates_session_id"), table_name="calendar_candidates")
    op.drop_index(op.f("ix_calendar_candidates_user_id"), table_name="calendar_candidates")
    op.drop_index(op.f("ix_calendar_candidates_id"), table_name="calendar_candidates")
    op.drop_table("calendar_candidates")
