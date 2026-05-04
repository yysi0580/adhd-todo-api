"""add routines

Revision ID: 20260505_0008
Revises: 20260505_0007
Create Date: 2026-05-05
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260505_0008"
down_revision: str | None = "20260505_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "routines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("micro_step", sa.Text(), nullable=False),
        sa.Column("effort_level", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_routines_id"), "routines", ["id"], unique=False)
    op.create_index(op.f("ix_routines_user_id"), "routines", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_routines_user_id"), table_name="routines")
    op.drop_index(op.f("ix_routines_id"), table_name="routines")
    op.drop_table("routines")
