import uuid
from enum import IntEnum
from typing import TYPE_CHECKING, List

import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field, Index, Relationship, SQLModel, desc, text

from app.core.base_model import DateTimeMixin

# 防止循环导入
if TYPE_CHECKING:
    from app.auth.model import Code, RefreshToken, Social_Account

# 定义用户角色的枚举类型


class RoleType(IntEnum):
    user = 1
    admin = 2


class User(DateTimeMixin, SQLModel, table=True):
    """用户表 - 存储系统用户的基本信息"""

    __tablename__ = "users"  # type: ignore[assignment]

    __table_args__ = (
        # 复合索引
        Index("idx_users_is_active_email", "is_active", "email"),  # 按是否激活+邮箱筛选
        Index(
            "idx_users_is_active_username", "is_active", "username"
        ),  # 按是否激活+用户名筛选
        Index(
            "idx_users_is_verified_email", "is_verified", "email"
        ),  # 按是否验证+邮箱筛选
        Index(
            "idx_users_is_verified_username", "is_verified", "username"
        ),  # 按是否验证+用户名筛选
        Index(
            "idx_users_is_deleted_email", "is_deleted", "email"
        ),  # 按是否删除+邮箱筛选
        Index(
            "idx_users_is_deleted_username", "is_deleted", "username"
        ),  # 按是否删除+用户名筛选
        # 排序索引
        Index("idx_users_created_at_desc", desc("created_at")),
        Index("idx_users_updated_at_desc", desc("updated_at")),
    )

    uid: uuid.UUID | None = Field(
        default=None,
        sa_column=Column(
            pg.UUID(as_uuid=True),
            server_default=text("gen_random_uuid()"),
            primary_key=True,
        ),
    )
    username: str | None = Field(
        default=None, max_length=30, unique=True, nullable=True
    )
    email: str = Field(
        ..., max_length=100, unique=True, nullable=False
    )  # email 必填，不可为空
    password_hash: str | None = Field(default=None, max_length=255)
    role: RoleType = Field(default=RoleType.user, nullable=False)
    bio: str | None = Field(default="这个人很懒，什么都没有留下。", max_length=300)
    ip_address: str | None = Field(default=None, max_length=45)
    longitude: float | None = Field(default=None)
    latitude: float | None = Field(default=None)
    city: str | None = Field(default=None, max_length=50)
    is_active: bool = Field(default=False, nullable=False)
    is_verified: bool = Field(default=False, nullable=False)
    is_deleted: bool = Field(default=False, nullable=False)

    # 关系字段定义
    # 1. 一对一关系：用户头像

    # 2. 一对多关系：用户创建的内容（可以级联删除）
    # 一对多关系：用户创建的内容（可以级联删除）
    refresh_tokens: List["RefreshToken"] = Relationship(passive_deletes=True)

    codes: List["Code"] = Relationship(passive_deletes=True)

    social_accounts: List["Social_Account"] = Relationship(passive_deletes=True)

    # 3. 一对多关系：重要业务数据（不应级联删除，支持软删除）

    # 4. 重要业务关系：绝对不能级联删除

    def __repr__(self):
        return f"<User(id={self.uid}, username={self.username})>"
