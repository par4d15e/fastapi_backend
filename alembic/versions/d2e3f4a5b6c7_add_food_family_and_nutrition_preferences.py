"""add food family and nutrition preferences

Revision ID: d2e3f4a5b6c7
Revises: f1a2b3c4d5e6
Create Date: 2026-03-29 07:30:00.000000
"""

from typing import Sequence, Union

from alembic import op
import fastapi_users_db_sqlalchemy
import sqlalchemy as sa


revision: str = "d2e3f4a5b6c7"
down_revision: Union[str, Sequence[str], None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "foods",
        sa.Column("family_id", sa.Integer(), nullable=True, comment="所属家庭ID"),
    )
    op.create_foreign_key(
        op.f("fk_foods_family_id"),
        "foods",
        "families",
        ["family_id"],
        ["id"],
    )
    op.create_index("idx_foods_family_id", "foods", ["family_id"], unique=False)

    op.create_table(
        "nutrition_preferences",
        sa.Column("id", sa.Integer(), nullable=False, comment="营养偏好ID"),
        sa.Column("profile_id", sa.Integer(), nullable=False, comment="宠物ID"),
        sa.Column(
            "selected_foods",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
            comment="最近一次选择的食品配置",
        ),
        sa.Column(
            "daily_kcals_target",
            sa.Float(),
            nullable=True,
            comment="最近一次目标热量",
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
            ["profile_id"], ["profiles.id"], name=op.f("fk_nutrition_preferences_profile_id")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_nutrition_preferences_id")),
        sa.UniqueConstraint("profile_id", name="uk_nutrition_preferences_profile_id"),
    )
    op.create_index(
        op.f("idx_nutrition_preferences_profile_id"),
        "nutrition_preferences",
        ["profile_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("idx_nutrition_preferences_profile_id"), table_name="nutrition_preferences"
    )
    op.drop_table("nutrition_preferences")

    op.drop_index("idx_foods_family_id", table_name="foods")
    op.drop_constraint(op.f("fk_foods_family_id"), "foods", type_="foreignkey")
    op.drop_column("foods", "family_id")
