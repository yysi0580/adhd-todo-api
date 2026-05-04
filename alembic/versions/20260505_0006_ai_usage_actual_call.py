"""track actual openai calls

Revision ID: 20260505_0006
Revises: 20260505_0005
Create Date: 2026-05-05
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260505_0006"
down_revision: str | None = "20260505_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "ai_usage_logs",
        sa.Column("actual_openai_call", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index(
        op.f("ix_ai_usage_logs_actual_openai_call"),
        "ai_usage_logs",
        ["actual_openai_call"],
        unique=False,
    )
    op.alter_column("ai_usage_logs", "actual_openai_call", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_ai_usage_logs_actual_openai_call"), table_name="ai_usage_logs")
    op.drop_column("ai_usage_logs", "actual_openai_call")
