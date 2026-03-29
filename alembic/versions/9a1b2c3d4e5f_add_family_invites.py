"""add family invites

Revision ID: 9a1b2c3d4e5f
Revises: d2e3f4a5b6c7
Create Date: 2026-03-29 08:10:00.000000
"""

from typing import Sequence, Union

from alembic import op
import fastapi_users_db_sqlalchemy
import sqlalchemy as sa


revision: str = "9a1b2c3d4e5f"
down_revision: Union[str, Sequence[str], None] = "d2e3f4a5b6c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "family_invites",
        sa.Column("id", sa.Integer(), nullable=False, comment="家庭邀请ID"),
        sa.Column("family_id", sa.Integer(), nullable=False, comment="家庭ID"),
        sa.Column("inviter_id", fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False, comment="邀请人ID"),
        sa.Column("token", sa.String(length=64), nullable=False, comment="邀请令牌"),
        sa.Column("accepted_user_id", fastapi_users_db_sqlalchemy.generics.GUID(), nullable=True, comment="接受邀请的用户ID"),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True, comment="接受时间"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True, comment="过期时间"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="创建时间（数据库自动生成）",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="更新时间（数据库自动生成/刷新）",
        ),
        sa.ForeignKeyConstraint(["family_id"], ["families.id"], name=op.f("fk_family_invites_family_id")),
        sa.ForeignKeyConstraint(["inviter_id"], ["users.id"], name=op.f("fk_family_invites_inviter_id")),
        sa.ForeignKeyConstraint(["accepted_user_id"], ["users.id"], name=op.f("fk_family_invites_accepted_user_id")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_family_invites_id")),
        sa.UniqueConstraint("token", name="uk_family_invites_token"),
    )
    op.create_index(op.f("idx_family_invites_family_invites_family_id"), "family_invites", ["family_id"], unique=False)
    op.create_index(op.f("idx_family_invites_family_invites_inviter_id"), "family_invites", ["inviter_id"], unique=False)
    op.create_index(op.f("idx_family_invites_family_invites_accepted_user_id"), "family_invites", ["accepted_user_id"], unique=False)
    op.create_index("idx_family_invites_created_at_desc", "family_invites", [sa.literal_column("created_at DESC")], unique=False)


def downgrade() -> None:
    op.drop_index("idx_family_invites_created_at_desc", table_name="family_invites")
    op.drop_index(op.f("idx_family_invites_family_invites_accepted_user_id"), table_name="family_invites")
    op.drop_index(op.f("idx_family_invites_family_invites_inviter_id"), table_name="family_invites")
    op.drop_index(op.f("idx_family_invites_family_invites_family_id"), table_name="family_invites")
    op.drop_table("family_invites")
