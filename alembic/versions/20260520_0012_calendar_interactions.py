"""add calendar interaction metadata

Revision ID: 20260520_0012
Revises: 20260520_0011
Create Date: 2026-05-20
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260520_0012"
down_revision: str | None = "20260520_0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("calendar_events", sa.Column("candidate_id", sa.Integer(), nullable=True))
    op.add_column(
        "calendar_events",
        sa.Column("status", sa.String(length=40), nullable=False, server_default="scheduled"),
    )
    op.add_column(
        "calendar_events",
        sa.Column("display_color", sa.String(length=40), nullable=True),
    )
    op.add_column(
        "calendar_events",
        sa.Column("is_soft_block", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column(
        "calendar_events",
        sa.Column("reschedule_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index(
        op.f("ix_calendar_events_candidate_id"),
        "calendar_events",
        ["candidate_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_calendar_events_candidate_id_calendar_candidates",
        "calendar_events",
        "calendar_candidates",
        ["candidate_id"],
        ["id"],
    )

    op.add_column(
        "calendar_candidates",
        sa.Column("calendar_event_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "calendar_candidates",
        sa.Column("planned_start_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "calendar_candidates",
        sa.Column("planned_end_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "calendar_candidates",
        sa.Column(
            "placement_source",
            sa.String(length=40),
            nullable=False,
            server_default="ai_suggested",
        ),
    )
    op.add_column(
        "calendar_candidates",
        sa.Column("is_locked", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "calendar_candidates",
        sa.Column("conflict_status", sa.String(length=40), nullable=False, server_default="clear"),
    )
    op.add_column("calendar_candidates", sa.Column("user_note", sa.Text(), nullable=True))
    op.create_index(
        op.f("ix_calendar_candidates_calendar_event_id"),
        "calendar_candidates",
        ["calendar_event_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_calendar_candidates_calendar_event_id"),
        table_name="calendar_candidates",
    )
    op.drop_column("calendar_candidates", "user_note")
    op.drop_column("calendar_candidates", "conflict_status")
    op.drop_column("calendar_candidates", "is_locked")
    op.drop_column("calendar_candidates", "placement_source")
    op.drop_column("calendar_candidates", "planned_end_at")
    op.drop_column("calendar_candidates", "planned_start_at")
    op.drop_column("calendar_candidates", "calendar_event_id")

    op.drop_constraint(
        "fk_calendar_events_candidate_id_calendar_candidates",
        "calendar_events",
        type_="foreignkey",
    )
    op.drop_index(op.f("ix_calendar_events_candidate_id"), table_name="calendar_events")
    op.drop_column("calendar_events", "reschedule_count")
    op.drop_column("calendar_events", "is_soft_block")
    op.drop_column("calendar_events", "display_color")
    op.drop_column("calendar_events", "status")
    op.drop_column("calendar_events", "candidate_id")
