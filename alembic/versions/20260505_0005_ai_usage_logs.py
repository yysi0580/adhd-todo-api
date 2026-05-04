"""add ai usage logs

Revision ID: 20260505_0005
Revises: 20260504_0004
Create Date: 2026-05-05
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260505_0005"
down_revision: str | None = "20260504_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_usage_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("feature_name", sa.String(length=80), nullable=False),
        sa.Column("model", sa.String(length=80), nullable=False),
        sa.Column("prompt_version", sa.String(length=40), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=False),
        sa.Column("cached_tokens", sa.Integer(), nullable=False),
        sa.Column("output_tokens", sa.Integer(), nullable=False),
        sa.Column("total_tokens", sa.Integer(), nullable=False),
        sa.Column("estimated_cost", sa.Float(), nullable=False),
        sa.Column("cache_hit", sa.Boolean(), nullable=False),
        sa.Column("source", sa.String(length=30), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("fallback_used", sa.Boolean(), nullable=False),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_usage_logs_id"), "ai_usage_logs", ["id"], unique=False)
    op.create_index(op.f("ix_ai_usage_logs_user_id"), "ai_usage_logs", ["user_id"], unique=False)
    op.create_index(
        op.f("ix_ai_usage_logs_feature_name"), "ai_usage_logs", ["feature_name"], unique=False
    )
    op.create_index(
        op.f("ix_ai_usage_logs_prompt_version"),
        "ai_usage_logs",
        ["prompt_version"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_ai_usage_logs_prompt_version"), table_name="ai_usage_logs")
    op.drop_index(op.f("ix_ai_usage_logs_feature_name"), table_name="ai_usage_logs")
    op.drop_index(op.f("ix_ai_usage_logs_user_id"), table_name="ai_usage_logs")
    op.drop_index(op.f("ix_ai_usage_logs_id"), table_name="ai_usage_logs")
    op.drop_table("ai_usage_logs")
