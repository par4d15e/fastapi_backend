"""add family tables

Revision ID: f1a2b3c4d5e6
Revises: 8f3ae3efc339
Create Date: 2026-03-29 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import fastapi_users_db_sqlalchemy
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "8f3ae3efc339"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """升级 schema。"""
    op.create_table(
        "families",
        sa.Column("id", sa.Integer(), nullable=False, comment="家庭ID"),
        sa.Column("name", sa.String(length=100), nullable=False, comment="家庭名称"),
        sa.Column(
            "owner_id",
            fastapi_users_db_sqlalchemy.generics.GUID(),
            nullable=False,
            comment="家庭创建者ID",
        ),
        sa.Column(
            "description",
            sa.String(length=255),
            nullable=True,
            comment="家庭描述",
        ),
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
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
            name=op.f("fk_families_owner_id"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_families_id")),
        sa.UniqueConstraint("name", name=op.f("uk_families_name")),
    )
    op.create_index(
        op.f("idx_families_families_created_at"),
        "families",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("idx_families_families_owner_id"),
        "families",
        ["owner_id"],
        unique=False,
    )
    op.create_index(
        "idx_families_created_at_desc",
        "families",
        [sa.literal_column("created_at DESC")],
        unique=False,
    )

    op.create_table(
        "family_members",
        sa.Column("id", sa.Integer(), nullable=False, comment="家庭成员ID"),
        sa.Column(
            "family_id",
            sa.Integer(),
            nullable=False,
            comment="家庭ID",
        ),
        sa.Column(
            "user_id",
            fastapi_users_db_sqlalchemy.generics.GUID(),
            nullable=False,
            comment="用户ID",
        ),
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
            comment="成员角色",
        ),
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
        sa.ForeignKeyConstraint(
            ["family_id"],
            ["families.id"],
            name=op.f("fk_family_members_family_id"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_family_members_user_id"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_family_members_id")),
        sa.UniqueConstraint(
            "family_id",
            "user_id",
            name="uk_family_members_family_id_user_id",
        ),
    )
    op.create_index(
        op.f("idx_family_members_family_members_created_at"),
        "family_members",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("idx_family_members_family_members_family_id"),
        "family_members",
        ["family_id"],
        unique=False,
    )
    op.create_index(
        op.f("idx_family_members_family_members_user_id"),
        "family_members",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "idx_family_members_created_at_desc",
        "family_members",
        [sa.literal_column("created_at DESC")],
        unique=False,
    )

    op.add_column(
        "profiles",
        sa.Column("family_id", sa.Integer(), nullable=True, comment="所属家庭ID"),
    )
    op.create_foreign_key(
        op.f("fk_profiles_family_id"),
        "profiles",
        "families",
        ["family_id"],
        ["id"],
    )
    op.create_index(
        op.f("idx_profiles_profiles_family_id"),
        "profiles",
        ["family_id"],
        unique=False,
    )


def downgrade() -> None:
    """降级 schema。"""
    op.drop_index(op.f("idx_profiles_profiles_family_id"), table_name="profiles")
    op.drop_constraint(op.f("fk_profiles_family_id"), "profiles", type_="foreignkey")
    op.drop_column("profiles", "family_id")

    op.drop_index(
        "idx_family_members_created_at_desc", table_name="family_members"
    )
    op.drop_index(
        op.f("idx_family_members_family_members_user_id"),
        table_name="family_members",
    )
    op.drop_index(
        op.f("idx_family_members_family_members_family_id"),
        table_name="family_members",
    )
    op.drop_index(
        op.f("idx_family_members_family_members_created_at"),
        table_name="family_members",
    )
    op.drop_table("family_members")

    op.drop_index("idx_families_created_at_desc", table_name="families")
    op.drop_index(op.f("idx_families_families_owner_id"), table_name="families")
    op.drop_index(op.f("idx_families_families_created_at"), table_name="families")
    op.drop_table("families")
