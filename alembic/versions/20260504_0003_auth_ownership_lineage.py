"""Add users, ownership, and suggestion lineage.

Revision ID: 20260504_0003
Revises: 20260503_0002
Create Date: 2026-05-04
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260504_0003"
down_revision: str | None = "20260503_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    is_sqlite = op.get_bind().dialect.name == "sqlite"
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    for table_name in ["sessions", "brain_dumps", "suggestions", "actions", "feedback"]:
        op.add_column(table_name, sa.Column("user_id", sa.Integer(), nullable=True))
        op.create_index(op.f(f"ix_{table_name}_user_id"), table_name, ["user_id"], unique=False)
        if not is_sqlite:
            op.create_foreign_key(
                f"fk_{table_name}_user_id_users",
                table_name,
                "users",
                ["user_id"],
                ["id"],
            )

    op.add_column("suggestions", sa.Column("parent_suggestion_id", sa.Integer(), nullable=True))
    op.add_column(
        "suggestions",
        sa.Column("generation_type", sa.String(length=30), nullable=True),
    )
    op.execute("UPDATE suggestions SET generation_type = 'original' WHERE generation_type IS NULL")
    if not is_sqlite:
        op.alter_column("suggestions", "generation_type", nullable=False)
    op.create_index(
        op.f("ix_suggestions_parent_suggestion_id"),
        "suggestions",
        ["parent_suggestion_id"],
        unique=False,
    )
    if not is_sqlite:
        op.create_foreign_key(
            "fk_suggestions_parent_suggestion_id_suggestions",
            "suggestions",
            "suggestions",
            ["parent_suggestion_id"],
            ["id"],
        )

    op.create_index(op.f("ix_brain_dumps_session_id"), "brain_dumps", ["session_id"], unique=False)
    op.create_index(op.f("ix_suggestions_session_id"), "suggestions", ["session_id"], unique=False)
    op.create_index(op.f("ix_actions_session_id"), "actions", ["session_id"], unique=False)
    op.create_index(op.f("ix_feedback_session_id"), "feedback", ["session_id"], unique=False)
    op.create_index(op.f("ix_feedback_suggestion_id"), "feedback", ["suggestion_id"], unique=False)
    op.create_index(op.f("ix_feedback_action_id"), "feedback", ["action_id"], unique=False)


def downgrade() -> None:
    is_sqlite = op.get_bind().dialect.name == "sqlite"
    op.drop_index(op.f("ix_feedback_action_id"), table_name="feedback")
    op.drop_index(op.f("ix_feedback_suggestion_id"), table_name="feedback")
    op.drop_index(op.f("ix_feedback_session_id"), table_name="feedback")
    op.drop_index(op.f("ix_actions_session_id"), table_name="actions")
    op.drop_index(op.f("ix_suggestions_session_id"), table_name="suggestions")
    op.drop_index(op.f("ix_brain_dumps_session_id"), table_name="brain_dumps")

    if not is_sqlite:
        op.drop_constraint(
            "fk_suggestions_parent_suggestion_id_suggestions",
            "suggestions",
            type_="foreignkey",
        )
    op.drop_index(op.f("ix_suggestions_parent_suggestion_id"), table_name="suggestions")
    op.drop_column("suggestions", "generation_type")
    op.drop_column("suggestions", "parent_suggestion_id")

    for table_name in ["feedback", "actions", "suggestions", "brain_dumps", "sessions"]:
        if not is_sqlite:
            op.drop_constraint(f"fk_{table_name}_user_id_users", table_name, type_="foreignkey")
        op.drop_index(op.f(f"ix_{table_name}_user_id"), table_name=table_name)
        op.drop_column(table_name, "user_id")

    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
