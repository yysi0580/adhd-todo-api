"""Add action finish metadata.

Revision ID: 20260503_0002
Revises: 20260503_0001
Create Date: 2026-05-03
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260503_0002"
down_revision: str | None = "20260503_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("actions", sa.Column("completion_note", sa.Text(), nullable=True))
    op.add_column("actions", sa.Column("abort_reason", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("actions", "abort_reason")
    op.drop_column("actions", "completion_note")
