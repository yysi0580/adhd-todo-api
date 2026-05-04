"""Add suggestion source.

Revision ID: 20260504_0004
Revises: 20260504_0003
Create Date: 2026-05-04
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260504_0004"
down_revision: str | None = "20260504_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "suggestions",
        sa.Column("source", sa.String(length=30), nullable=True),
    )
    op.execute("UPDATE suggestions SET source = 'rule_based' WHERE source IS NULL")
    if op.get_bind().dialect.name != "sqlite":
        op.alter_column("suggestions", "source", nullable=False)
    op.create_index(op.f("ix_suggestions_source"), "suggestions", ["source"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_suggestions_source"), table_name="suggestions")
    op.drop_column("suggestions", "source")
